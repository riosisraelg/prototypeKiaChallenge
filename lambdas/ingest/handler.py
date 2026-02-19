"""
Lambda handler for ingesting IoT sensor data.

This Lambda function receives events from AWS IoT Rules Engine, validates
the payload, enriches it with metadata, stores it in DynamoDB, and publishes
events to EventBridge for further processing.

Requirements: 3.1, 3.2, 4.5
"""

import json
import os
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError

# Import validators from the same package
from validators import validate_message, ValidationError

# Import metrics client
import sys
sys.path.append('/opt/python')  # Lambda layer path
try:
    from common.metrics import MetricsClient
except ImportError:
    # Fallback if common module not available
    logger.warning("Could not import MetricsClient, metrics will be limited")
    MetricsClient = None

# Configure logging
logger = logging.getLogger()
log_level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, log_level))

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

# Environment variables
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'kia-paintshop-sensor-data')
EVENTBRIDGE_BUS = os.environ.get('EVENTBRIDGE_BUS', 'default')
TTL_DAYS = int(os.environ.get('TTL_DAYS', '30'))

# Get DynamoDB table
table = dynamodb.Table(DYNAMODB_TABLE)


class IngestError(Exception):
    """Base exception for ingestion errors."""
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


def enrich_message(message: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Enrich message with additional metadata.
    
    Args:
        message: Validated message dict
        context: Lambda context object
        
    Returns:
        Enriched message dict
    """
    enriched = message.copy()
    
    # Add processing metadata
    enriched['request_id'] = context.request_id
    enriched['processing_timestamp'] = datetime.utcnow().isoformat() + 'Z'
    enriched['ingestion_time_ms'] = int(time.time() * 1000)
    
    return enriched


def build_dynamodb_item(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build DynamoDB item from enriched message.
    
    Item structure follows design specification:
    - PK: "{area}#{variable_id}"
    - SK: "DATA#{timestamp_ms}"
    - TTL: 30 days from now
    
    Args:
        message: Enriched message dict
        
    Returns:
        DynamoDB item dict
    """
    # Parse timestamp to get milliseconds
    timestamp_str = message['timestamp']
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        timestamp_ms = int(dt.timestamp() * 1000)
    except (ValueError, AttributeError) as e:
        logger.error(f"Failed to parse timestamp: {e}")
        timestamp_ms = int(time.time() * 1000)
    
    # Build partition and sort keys
    pk = f"{message['area']}#{message['variable_id']}"
    sk = f"DATA#{timestamp_ms}"
    
    # Build item
    item = {
        'PK': pk,
        'SK': sk,
        'variable_id': message['variable_id'],
        'area': message['area'],
        'timestamp': message['timestamp'],
        'value': message['value'],
        'unit': message['unit'],
        'quality': message.get('quality', 'good'),
        'request_id': message.get('request_id', ''),
        'processing_timestamp': message.get('processing_timestamp', ''),
        'ttl': calculate_ttl(TTL_DAYS)
    }
    
    # Add metadata if present
    if 'metadata' in message:
        item['metadata'] = message['metadata']
    
    return item


def store_in_dynamodb(item: Dict[str, Any], max_retries: int = 3) -> bool:
    """
    Store item in DynamoDB with retry logic.
    
    Args:
        item: DynamoDB item to store
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        IngestError: If storage fails after retries
    """
    for attempt in range(max_retries):
        try:
            table.put_item(Item=item)
            logger.info(f"Stored item in DynamoDB: PK={item['PK']}, SK={item['SK']}")
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
                logger.error(f"DynamoDB table not found: {DYNAMODB_TABLE}")
                raise IngestError(f"Table {DYNAMODB_TABLE} does not exist")
                
            else:
                # Other errors - log and retry
                logger.error(f"DynamoDB error: {error_code} - {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise IngestError(f"Failed to store in DynamoDB after {max_retries} attempts: {e}")
                    
        except Exception as e:
            logger.error(f"Unexpected error storing in DynamoDB: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise IngestError(f"Failed to store in DynamoDB: {e}")
    
    return False


def publish_to_eventbridge(message: Dict[str, Any], max_retries: int = 3) -> bool:
    """
    Publish event to EventBridge for further processing.
    
    Args:
        message: Message to publish
        max_retries: Maximum number of retry attempts
        
    Returns:
        True if successful, False otherwise
    """
    event_detail = {
        'variable_id': message['variable_id'],
        'area': message['area'],
        'timestamp': message['timestamp'],
        'value': message['value'],
        'unit': message['unit'],
        'metadata': message.get('metadata', {}),
        'request_id': message.get('request_id', '')
    }
    
    event_entry = {
        'Source': 'kia.paintshop.ingest',
        'DetailType': 'SensorDataIngested',
        'Detail': json.dumps(event_detail),
        'EventBusName': EVENTBRIDGE_BUS
    }
    
    for attempt in range(max_retries):
        try:
            response = eventbridge.put_events(Entries=[event_entry])
            
            # Check if event was successfully published
            if response['FailedEntryCount'] == 0:
                logger.info(f"Published event to EventBridge for variable {message['variable_id']}")
                return True
            else:
                logger.error(f"Failed to publish event: {response['Entries'][0].get('ErrorMessage', 'Unknown error')}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    
        except ClientError as e:
            logger.error(f"EventBridge error: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                logger.error(f"Failed to publish to EventBridge after {max_retries} attempts")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error publishing to EventBridge: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                return False
    
    return False


def send_cloudwatch_metric(metric_name: str, value: float, unit: str = 'Count'):
    """
    Send custom metric to CloudWatch.
    
    Args:
        metric_name: Name of the metric
        value: Metric value
        unit: Metric unit (default: Count)
    """
    try:
        cloudwatch = boto3.client('cloudwatch')
        cloudwatch.put_metric_data(
            Namespace='KIA/PaintShop',
            MetricData=[{
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }]
        )
    except Exception as e:
        logger.warning(f"Failed to send CloudWatch metric: {e}")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for ingesting IoT sensor data.
    
    This function:
    1. Validates the incoming message payload
    2. Enriches it with metadata (request_id, processing_timestamp)
    3. Stores it in DynamoDB with 30-day TTL
    4. Publishes event to EventBridge for further processing
    5. Handles errors with retry logic
    
    Args:
        event: Event from IoT Rules Engine containing sensor data
        context: Lambda context object
        
    Returns:
        Dict with status and processing details
    """
    start_time = time.time()
    
    # Initialize metrics client
    metrics = MetricsClient('ingest') if MetricsClient else None
    
    try:
        logger.info(f"Processing event: {json.dumps(event)}")
        
        # Extract payload from IoT Rule event
        # IoT Rules Engine passes the message directly
        payload = event
        
        # Step 1: Validate message
        is_valid, error_message, validated_message = validate_message(payload)
        
        if not is_valid:
            logger.error(f"Validation failed: {error_message}")
            if metrics:
                metrics.put_error_metric('Ingest', 'ValidationError')
                metrics.flush()
            else:
                send_cloudwatch_metric('ValidationErrors', 1)
            
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': error_message
                    },
                    'request_id': context.request_id
                })
            }
        
        # Step 2: Enrich message with metadata
        enriched_message = enrich_message(validated_message, context)
        
        # Step 3: Build DynamoDB item
        dynamodb_item = build_dynamodb_item(enriched_message)
        
        # Step 4: Store in DynamoDB
        try:
            store_in_dynamodb(dynamodb_item)
            if metrics:
                metrics.put_metric('MessagesProcessed', 1, unit='Count')
            else:
                send_cloudwatch_metric('MessagesIngested', 1)
        except IngestError as e:
            logger.error(f"Failed to store in DynamoDB: {e}")
            if metrics:
                metrics.put_error_metric('Ingest', 'DynamoDBError')
                metrics.flush()
            else:
                send_cloudwatch_metric('DynamoDBErrors', 1)
            
            # Return error but don't fail completely
            # Lambda will retry based on DLQ configuration
            raise
        
        # Step 5: Publish to EventBridge (best effort)
        # Don't fail if EventBridge publish fails
        eventbridge_success = publish_to_eventbridge(enriched_message)
        if not eventbridge_success:
            logger.warning("Failed to publish to EventBridge, but data was stored in DynamoDB")
            if metrics:
                metrics.put_error_metric('Ingest', 'EventBridgeError')
            else:
                send_cloudwatch_metric('EventBridgeErrors', 1)
        
        # Calculate processing time
        processing_time_ms = (time.time() - start_time) * 1000
        
        if metrics:
            metrics.put_success_metric('Ingest')
            metrics.put_latency_metric('Ingest', processing_time_ms)
            metrics.flush()
        else:
            send_cloudwatch_metric('ProcessingTimeMs', processing_time_ms, 'Milliseconds')
        
        logger.info(f"Successfully processed message for variable {validated_message['variable_id']} in {processing_time_ms:.2f}ms")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'success': True,
                'data': {
                    'variable_id': validated_message['variable_id'],
                    'area': validated_message['area'],
                    'timestamp': validated_message['timestamp'],
                    'stored': True,
                    'eventbridge_published': eventbridge_success
                },
                'request_id': context.request_id,
                'processing_time_ms': processing_time_ms
            })
        }
        
    except IngestError as e:
        # Permanent errors - don't retry
        logger.error(f"Ingestion error: {e}")
        if metrics:
            metrics.put_error_metric('Ingest', 'IngestError')
            metrics.flush()
        else:
            send_cloudwatch_metric('IngestErrors', 1)
        
        return {
            'statusCode': 500,
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'INGEST_ERROR',
                    'message': str(e)
                },
                'request_id': context.request_id
            })
        }
        
    except Exception as e:
        # Unexpected errors - log and allow Lambda to retry
        logger.exception(f"Unexpected error: {e}")
        if metrics:
            metrics.put_error_metric('Ingest', 'UnexpectedError')
            metrics.flush()
        else:
            send_cloudwatch_metric('UnexpectedErrors', 1)
        
        # Re-raise to trigger Lambda retry and DLQ
        raise
