"""
Lambda handler for processing sensor data and detecting anomalies.

This Lambda function receives events from EventBridge (published by the ingest Lambda),
executes the anomaly detector to check for threshold violations, and stores alarms
in DynamoDB when anomalies are detected.

Requirements: 4.2, 4.3
"""

import json
import os
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Import anomaly detector from the same package
from anomaly_detector import AnomalyDetector, AlarmResult

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
ALARMS_TABLE = os.environ.get('ALARMS_TABLE', 'kia-paintshop-alarms')
VARIABLES_METADATA_TABLE = os.environ.get('VARIABLES_METADATA_TABLE', 'kia-paintshop-variables-metadata')

# Get DynamoDB tables
alarms_table = dynamodb.Table(ALARMS_TABLE)
variables_table = dynamodb.Table(VARIABLES_METADATA_TABLE)

# Initialize anomaly detector
detector = AnomalyDetector()


class ProcessError(Exception):
    """Base exception for processing errors."""
    pass


def get_variable_metadata(variable_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve variable metadata from DynamoDB.
    
    Args:
        variable_id: Variable ID to look up
        
    Returns:
        Variable metadata dict or None if not found
    """
    try:
        pk = f"VAR#{variable_id}"
        response = variables_table.get_item(
            Key={
                'PK': pk,
                'SK': 'METADATA'
            }
        )
        
        if 'Item' in response:
            logger.debug(f"Retrieved metadata for variable {variable_id}")
            return response['Item']
        else:
            logger.warning(f"No metadata found for variable {variable_id}")
            return None
            
    except ClientError as e:
        logger.error(f"Error retrieving variable metadata: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error retrieving metadata: {e}")
        return None


def create_alarm_record(
    variable_id: str,
    area: str,
    alarm_result: AlarmResult,
    timestamp: str,
    variable_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create alarm record for DynamoDB.
    
    Args:
        variable_id: Variable ID that triggered the alarm
        area: Area of the variable
        alarm_result: AlarmResult from anomaly detector
        timestamp: Timestamp of the sensor reading
        variable_name: Optional variable name for display
        
    Returns:
        DynamoDB alarm item dict
    """
    # Generate unique alarm ID
    alarm_id = str(uuid.uuid4())
    
    # Current timestamp for created_at
    created_at = datetime.utcnow().isoformat() + 'Z'
    
    # Build alarm item
    alarm_item = {
        'PK': f"ALARM#{alarm_id}",
        'SK': 'METADATA',
        'alarm_id': alarm_id,
        'variable_id': variable_id,
        'area': area,
        'severity': alarm_result.severity.value,
        'status': 'active',
        'message': alarm_result.message,
        'value': alarm_result.value,
        'threshold': alarm_result.threshold_value,
        'threshold_type': alarm_result.threshold_type,
        'exceedance_percent': round(alarm_result.exceedance_percent, 2),
        'created_at': created_at,
        'sensor_timestamp': timestamp
    }
    
    # Add optional variable name
    if variable_name:
        alarm_item['variable_name'] = variable_name
    
    return alarm_item


def store_alarm(alarm_item: Dict[str, Any], max_retries: int = 3) -> bool:
    """
    Store alarm in DynamoDB with retry logic.
    
    Args:
        alarm_item: Alarm item to store
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ProcessError: If storage fails after retries
    """
    for attempt in range(max_retries):
        try:
            alarms_table.put_item(Item=alarm_item)
            logger.info(f"Stored alarm in DynamoDB: alarm_id={alarm_item['alarm_id']}, "
                       f"variable={alarm_item['variable_id']}, severity={alarm_item['severity']}")
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
                logger.error(f"DynamoDB table not found: {ALARMS_TABLE}")
                raise ProcessError(f"Table {ALARMS_TABLE} does not exist")
                
            else:
                # Other errors - log and retry
                logger.error(f"DynamoDB error: {error_code} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise ProcessError(f"Failed to store alarm after {max_retries} attempts: {e}")
                    
        except Exception as e:
            logger.error(f"Unexpected error storing alarm: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise ProcessError(f"Failed to store alarm: {e}")
    
    return False


def send_cloudwatch_metric(metric_name: str, value: float, unit: str = 'Count', dimensions: Optional[Dict[str, str]] = None):
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


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing sensor data and detecting anomalies.
    
    This function:
    1. Receives events from EventBridge (published by ingest Lambda)
    2. Retrieves variable metadata (thresholds) from DynamoDB
    3. Executes anomaly detector to check for threshold violations
    4. If alarm detected, creates record in DynamoDB alarms table
    5. Generates unique alarm_id (UUID)
    6. Sets initial status as 'active'
    7. Registers metrics for alarms generated
    
    Args:
        event: EventBridge event containing sensor data
        context: Lambda context object
        
    Returns:
        Dict with processing status and alarm details
    """
    start_time = time.time()
    
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Extract sensor data from EventBridge event
        # EventBridge wraps the detail in a 'detail' field
        if 'detail' in event:
            sensor_data = event['detail']
        else:
            # Direct invocation for testing
            sensor_data = event
        
        # Extract required fields
        variable_id = sensor_data.get('variable_id')
        area = sensor_data.get('area')
        value = sensor_data.get('value')
        timestamp = sensor_data.get('timestamp')
        unit = sensor_data.get('unit')
        
        if not all([variable_id, area, value is not None, timestamp]):
            logger.error(f"Missing required fields in event: {sensor_data}")
            send_cloudwatch_metric('ProcessingErrors', 1)
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': 'Missing required fields',
                    'request_id': context.request_id
                })
            }
        
        # Step 1: Retrieve variable metadata to get thresholds
        metadata = get_variable_metadata(variable_id)
        
        if not metadata:
            logger.warning(f"No metadata found for variable {variable_id}, skipping anomaly detection")
            send_cloudwatch_metric('MetadataNotFound', 1)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'alarm_generated': False,
                    'reason': 'No metadata found',
                    'request_id': context.request_id
                })
            }
        
        # Extract thresholds from metadata
        alarm_low = metadata.get('alarm_low')
        alarm_high = metadata.get('alarm_high')
        min_range = metadata.get('min_range')
        max_range = metadata.get('max_range')
        variable_name = metadata.get('name')
        
        if alarm_low is None or alarm_high is None:
            logger.warning(f"No alarm thresholds defined for variable {variable_id}")
            send_cloudwatch_metric('NoThresholds', 1)
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'alarm_generated': False,
                    'reason': 'No thresholds defined',
                    'request_id': context.request_id
                })
            }
        
        # Step 2: Execute anomaly detector
        alarm_result = detector.detect(
            value=value,
            alarm_low=alarm_low,
            alarm_high=alarm_high,
            min_range=min_range,
            max_range=max_range,
            variable_name=variable_name or variable_id,
            unit=unit
        )
        
        # Step 3: If alarm detected, create record in DynamoDB
        if alarm_result.is_alarm:
            logger.info(f"Alarm detected for variable {variable_id}: {alarm_result.message}")
            
            # Create alarm record
            alarm_item = create_alarm_record(
                variable_id=variable_id,
                area=area,
                alarm_result=alarm_result,
                timestamp=timestamp,
                variable_name=variable_name
            )
            
            # Store alarm in DynamoDB
            try:
                store_alarm(alarm_item)
                
                # Send metrics
                send_cloudwatch_metric('AlarmsGenerated', 1)
                send_cloudwatch_metric(
                    'AlarmsBySeverity',
                    1,
                    dimensions={'Severity': alarm_result.severity.value}
                )
                send_cloudwatch_metric(
                    'AlarmsByArea',
                    1,
                    dimensions={'Area': area}
                )
                
                # Calculate processing time
                processing_time_ms = (time.time() - start_time) * 1000
                send_cloudwatch_metric('ProcessingTimeMs', processing_time_ms, 'Milliseconds')
                
                logger.info(f"Successfully processed alarm for variable {variable_id} in {processing_time_ms:.2f}ms")
                
                return {
                    'statusCode': 200,
                    'body': json.dumps({
                        'success': True,
                        'alarm_generated': True,
                        'alarm': {
                            'alarm_id': alarm_item['alarm_id'],
                            'variable_id': variable_id,
                            'severity': alarm_result.severity.value,
                            'message': alarm_result.message,
                            'value': value,
                            'threshold': alarm_result.threshold_value,
                            'exceedance_percent': alarm_result.exceedance_percent
                        },
                        'request_id': context.request_id,
                        'processing_time_ms': processing_time_ms
                    })
                }
                
            except ProcessError as e:
                logger.error(f"Failed to store alarm: {e}")
                send_cloudwatch_metric('AlarmStorageErrors', 1)
                raise
        
        else:
            # No alarm detected
            logger.debug(f"No alarm for variable {variable_id}, value {value} within thresholds [{alarm_low}, {alarm_high}]")
            send_cloudwatch_metric('DataPointsProcessed', 1)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'success': True,
                    'alarm_generated': False,
                    'reason': 'Value within thresholds',
                    'request_id': context.request_id,
                    'processing_time_ms': processing_time_ms
                })
            }
        
    except ProcessError as e:
        # Permanent errors - don't retry
        logger.error(f"Processing error: {e}")
        send_cloudwatch_metric('ProcessErrors', 1)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'PROCESS_ERROR',
                    'message': str(e)
                },
                'request_id': context.request_id
            })
        }
        
    except Exception as e:
        # Unexpected errors - log and allow Lambda to retry
        logger.exception(f"Unexpected error: {e}")
        send_cloudwatch_metric('UnexpectedErrors', 1)
        
        # Re-raise to trigger Lambda retry
        raise
