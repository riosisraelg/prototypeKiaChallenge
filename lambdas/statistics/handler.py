"""
Lambda handler for calculating statistics for sensor data.

This Lambda function is triggered by EventBridge every 5 minutes.
For each active variable, it:
1. Queries sensor data from the last 10 minutes
2. Calculates statistics (avg, min, max, stddev)
3. Stores results in DynamoDB statistics table with 7-day TTL
4. Registers metrics to CloudWatch

Requirements: 4.1, 5.5
"""

import json
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal

# Import statistics calculator from the same package
from statistics_calculator import StatisticsCalculator

# Import metrics client
import sys
sys.path.append('/opt/python')  # Lambda layer path
try:
    from common.metrics import MetricsClient
except ImportError:
    logger.warning("Could not import MetricsClient, metrics will be limited")
    MetricsClient = None

# Configure logging
logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, log_level))

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

# Environment variables
SENSOR_DATA_TABLE = os.environ.get('SENSOR_DATA_TABLE', 'kia-paintshop-sensor-data')
STATISTICS_TABLE = os.environ.get('STATISTICS_TABLE', 'kia-paintshop-statistics')
VARIABLES_METADATA_TABLE = os.environ.get('VARIABLES_METADATA_TABLE', 'kia-paintshop-variables-metadata')
WINDOW_MINUTES = int(os.environ.get('WINDOW_MINUTES', '10'))
TTL_DAYS = int(os.environ.get('TTL_DAYS', '7'))

# Get DynamoDB tables
sensor_data_table = dynamodb.Table(SENSOR_DATA_TABLE)
statistics_table = dynamodb.Table(STATISTICS_TABLE)
variables_table = dynamodb.Table(VARIABLES_METADATA_TABLE)

# Initialize statistics calculator
calculator = StatisticsCalculator()


class StatisticsError(Exception):
    """Base exception for statistics processing errors."""
    pass


def calculate_ttl(days: int = TTL_DAYS) -> int:
    """
    Calculate TTL timestamp (epoch seconds) for DynamoDB.
    
    Args:
        days: Number of days until expiration
        
    Returns:
        Epoch timestamp in seconds
    """
    expiration = datetime.utcnow() + timedelta(days=days)
    return int(expiration.timestamp())


def get_active_variables() -> List[Dict[str, Any]]:
    """
    Retrieve all active variables from DynamoDB.
    
    Returns:
        List of variable metadata dictionaries
    """
    try:
        # Scan for active variables
        # Note: In production, consider using GSI or caching for better performance
        response = variables_table.scan(
            FilterExpression='active = :active',
            ExpressionAttributeValues={':active': True}
        )
        
        variables = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = variables_table.scan(
                FilterExpression='active = :active',
                ExpressionAttributeValues={':active': True},
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            variables.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(variables)} active variables")
        return variables
        
    except ClientError as e:
        logger.error(f"Error retrieving active variables: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error retrieving variables: {e}")
        return []


def query_sensor_data(
    area: str,
    variable_id: str,
    start_time: datetime,
    end_time: datetime
) -> List[Dict[str, Any]]:
    """
    Query sensor data for a variable within a time range.
    
    Args:
        area: Variable area
        variable_id: Variable ID
        start_time: Start of time window
        end_time: End of time window
        
    Returns:
        List of sensor data items
    """
    try:
        # Build partition key
        pk = f"{area}#{variable_id}"
        
        # Convert timestamps to milliseconds for sort key
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        # Query DynamoDB
        response = sensor_data_table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :start_sk AND :end_sk',
            ExpressionAttributeValues={
                ':pk': pk,
                ':start_sk': f"DATA#{start_ms}",
                ':end_sk': f"DATA#{end_ms}"
            }
        )
        
        items = response.get('Items', [])
        
        logger.debug(f"Retrieved {len(items)} data points for {variable_id} in time range")
        return items
        
    except ClientError as e:
        logger.error(f"Error querying sensor data for {variable_id}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error querying sensor data: {e}")
        return []


def store_statistics(
    variable_id: str,
    area: str,
    window_start: datetime,
    window_end: datetime,
    stats_result: Any,
    max_retries: int = 3
) -> bool:
    """
    Store calculated statistics in DynamoDB.
    
    Args:
        variable_id: Variable ID
        area: Variable area
        window_start: Start of time window
        window_end: End of time window
        stats_result: StatisticsResult object
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if successful, False otherwise
    """
    # Build item
    item = {
        'PK': variable_id,
        'SK': f"STATS#{window_start.isoformat()}Z",
        'variable_id': variable_id,
        'area': area,
        'window_start': window_start.isoformat() + 'Z',
        'window_end': window_end.isoformat() + 'Z',
        'window_minutes': WINDOW_MINUTES,
        'count': stats_result.count,
        'ttl': calculate_ttl(TTL_DAYS)
    }
    
    # Add statistics if valid
    if stats_result.is_valid:
        # Convert to Decimal for DynamoDB
        item['avg'] = Decimal(str(round(stats_result.avg, 2)))
        item['min'] = Decimal(str(round(stats_result.min, 2)))
        item['max'] = Decimal(str(round(stats_result.max, 2)))
        item['stddev'] = Decimal(str(round(stats_result.stddev, 2)))
        item['is_valid'] = True
    else:
        item['is_valid'] = False
        item['error_message'] = stats_result.error_message
    
    # Store with retry logic
    for attempt in range(max_retries):
        try:
            statistics_table.put_item(Item=item)
            logger.info(f"Stored statistics for {variable_id}: count={stats_result.count}, valid={stats_result.is_valid}")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            
            if error_code == 'ProvisionedThroughputExceededException':
                # Throttling - retry with exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"DynamoDB throttling, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                
            elif error_code == 'ResourceNotFoundException':
                # Table doesn't exist - permanent error
                logger.error(f"DynamoDB table not found: {STATISTICS_TABLE}")
                raise StatisticsError(f"Table {STATISTICS_TABLE} does not exist")
                
            else:
                # Other errors - log and retry
                logger.error(f"DynamoDB error: {error_code} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise StatisticsError(f"Failed to store statistics after {max_retries} attempts: {e}")
                    
        except Exception as e:
            logger.error(f"Unexpected error storing statistics: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise StatisticsError(f"Failed to store statistics: {e}")
    
    return False


def send_cloudwatch_metric(
    metric_name: str,
    value: float,
    unit: str = 'Count',
    dimensions: Optional[Dict[str, str]] = None
):
    """
    Send custom metric to CloudWatch.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Metric unit (default: Count)
        dimensions: Optional metric dimensions
    """
    try:
        metric_data = {
            'MetricName': metric_name,
            'Value': value,
            'Unit': unit,
            'Timestamp': datetime.utcnow()
        }
        
        if dimensions:
            metric_data['Dimensions'] = [
                {'Name': k, 'Value': v} for k, v in dimensions.items()
            ]
        
        cloudwatch.put_metric_data(
            Namespace='KIA/PaintShop',
            MetricData=[metric_data]
        )
    except Exception as e:
        logger.warning(f"Failed to send CloudWatch metric: {e}")


def process_variable_statistics(
    variable: Dict[str, Any],
    window_start: datetime,
    window_end: datetime
) -> Dict[str, Any]:
    """
    Process statistics for a single variable.
    
    Args:
        variable: Variable metadata dictionary
        window_start: Start of time window
        window_end: End of time window
        
    Returns:
        Dict with processing results
    """
    variable_id = variable.get('variable_id')
    area = variable.get('area')
    
    if not variable_id or not area:
        logger.warning(f"Variable missing required fields: {variable}")
        return {
            'variable_id': variable_id,
            'success': False,
            'error': 'Missing required fields'
        }
    
    try:
        # Step 1: Query sensor data for the time window
        sensor_data = query_sensor_data(area, variable_id, window_start, window_end)
        
        # Step 2: Calculate statistics
        stats_result = calculator.calculate_from_data_points(sensor_data, value_key='value')
        
        # Step 3: Store statistics in DynamoDB
        if stats_result.count > 0:
            store_statistics(variable_id, area, window_start, window_end, stats_result)
            
            # Send metrics
            if stats_result.is_valid:
                send_cloudwatch_metric('StatisticsCalculated', 1)
                send_cloudwatch_metric(
                    'DataPointsProcessed',
                    stats_result.count,
                    dimensions={'VariableId': variable_id}
                )
            else:
                send_cloudwatch_metric('InsufficientDataPoints', 1)
        else:
            logger.debug(f"No data points found for {variable_id} in time window")
            send_cloudwatch_metric('NoDataPoints', 1)
        
        return {
            'variable_id': variable_id,
            'success': True,
            'count': stats_result.count,
            'is_valid': stats_result.is_valid
        }
        
    except StatisticsError as e:
        logger.error(f"Statistics error for {variable_id}: {e}")
        send_cloudwatch_metric('StatisticsErrors', 1)
        return {
            'variable_id': variable_id,
            'success': False,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Unexpected error processing {variable_id}: {e}")
        send_cloudwatch_metric('UnexpectedErrors', 1)
        return {
            'variable_id': variable_id,
            'success': False,
            'error': str(e)
        }


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for calculating statistics.
    
    This function is triggered by EventBridge every 5 minutes.
    For each active variable:
    1. Queries sensor data from the last 10 minutes
    2. Calculates statistics (avg, min, max, stddev)
    3. Stores results in DynamoDB with 7-day TTL
    4. Registers metrics to CloudWatch
    
    Args:
        event: EventBridge scheduled event
        context: Lambda context object
        
    Returns:
        Dict with processing summary
    """
    start_time = time.time()
    
    try:
        logger.info("Starting statistics calculation")
        
        # Define time window (last 10 minutes)
        window_end = datetime.utcnow()
        window_start = window_end - timedelta(minutes=WINDOW_MINUTES)
        
        logger.info(f"Time window: {window_start.isoformat()}Z to {window_end.isoformat()}Z")
        
        # Step 1: Get all active variables
        variables = get_active_variables()
        
        if not variables:
            logger.warning("No active variables found")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'message': 'No active variables to process',
                    'variables_processed': 0,
                    'request_id': context.request_id
                })
            }
        
        # Step 2: Process each variable
        results = []
        success_count = 0
        error_count = 0
        
        for variable in variables:
            result = process_variable_statistics(variable, window_start, window_end)
            results.append(result)
            
            if result['success']:
                success_count += 1
            else:
                error_count += 1
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        # Send summary metrics
        send_cloudwatch_metric('VariablesProcessed', len(variables))
        send_cloudwatch_metric('SuccessfulCalculations', success_count)
        send_cloudwatch_metric('FailedCalculations', error_count)
        send_cloudwatch_metric('ProcessingTimeMs', processing_time_ms, 'Milliseconds')
        
        logger.info(
            f"Statistics calculation completed: {success_count} successful, "
            f"{error_count} errors, {processing_time_ms:.2f}ms"
        )
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'variables_processed': len(variables),
                'successful': success_count,
                'failed': error_count,
                'window_start': window_start.isoformat() + 'Z',
                'window_end': window_end.isoformat() + 'Z',
                'processing_time_ms': processing_time_ms,
                'request_id': context.request_id
            })
        }
        
    except Exception as e:
        # Unexpected errors - log and return error
        logger.exception(f"Unexpected error in statistics handler: {e}")
        send_cloudwatch_metric('HandlerErrors', 1)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'HANDLER_ERROR',
                    'message': str(e)
                },
                'request_id': context.request_id
            })
        }
