"""
Lambda handler for GET /variables/{id}/data endpoint.

This handler retrieves historical sensor data for a specific variable within
a time range. It queries DynamoDB first (recent data with 30-day TTL), and
falls back to S3 for older archived data if needed.

The sensor-data table uses:
- PK = "{area}#{variable_id}"
- SK = "DATA#{timestamp_ms}"

This allows efficient range queries by variable and time.

Requirements: 5.2, 3.3
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# Environment variables
SENSOR_DATA_TABLE = os.environ.get('SENSOR_DATA_TABLE', 'kia-paintshop-sensor-data')
VARIABLES_METADATA_TABLE = os.environ.get('VARIABLES_METADATA_TABLE', 'kia-paintshop-variables-metadata')
ARCHIVE_BUCKET = os.environ.get('ARCHIVE_BUCKET', '')

# Get DynamoDB tables
sensor_data_table = dynamodb.Table(SENSOR_DATA_TABLE)
variables_metadata_table = dynamodb.Table(VARIABLES_METADATA_TABLE)


class ValidationError(Exception):
    """Validation error for request parameters."""
    pass


def parse_iso8601_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO 8601 timestamp string to datetime object.
    
    Args:
        timestamp_str: ISO 8601 timestamp string
        
    Returns:
        datetime object in UTC
        
    Raises:
        ValidationError: If timestamp format is invalid
    """
    try:
        # Handle both with and without 'Z' suffix
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        dt = datetime.fromisoformat(timestamp_str)
        
        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except (ValueError, AttributeError) as e:
        raise ValidationError(f"Formato de timestamp inválido: {timestamp_str}. Use formato ISO 8601 (ej: 2024-01-15T10:30:00Z)")


def validate_query_params(event: Dict[str, Any]) -> tuple[str, datetime, datetime]:
    """
    Validate and extract query parameters from API Gateway event.
    
    Args:
        event: API Gateway event
        
    Returns:
        Tuple of (variable_id, start_datetime, end_datetime)
        
    Raises:
        ValidationError: If parameters are invalid or missing
    """
    # Extract variable_id from path parameters
    path_params = event.get('pathParameters', {})
    
    variable_id = path_params.get('id') if path_params else None
    if not variable_id:
        raise ValidationError("ID de variable requerido en la ruta")
    
    # Extract query parameters
    query_params = event.get('queryStringParameters', {})
    if not query_params:
        raise ValidationError("Parámetros de consulta 'start' y 'end' son requeridos")
    
    start_str = query_params.get('start')
    end_str = query_params.get('end')
    
    if not start_str:
        raise ValidationError("Parámetro 'start' es requerido (formato ISO 8601)")
    
    if not end_str:
        raise ValidationError("Parámetro 'end' es requerido (formato ISO 8601)")
    
    # Parse timestamps
    start_dt = parse_iso8601_timestamp(start_str)
    end_dt = parse_iso8601_timestamp(end_str)
    
    # Validate time range
    if start_dt >= end_dt:
        raise ValidationError("El timestamp 'start' debe ser anterior a 'end'")
    
    # Validate range is not too large (max 7 days to prevent excessive data)
    max_range_days = 7
    range_days = (end_dt - start_dt).days
    if range_days > max_range_days:
        raise ValidationError(f"El rango de tiempo no puede exceder {max_range_days} días")
    
    return variable_id, start_dt, end_dt


def get_variable_metadata(variable_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve variable metadata from DynamoDB.
    
    Args:
        variable_id: Variable ID
        
    Returns:
        Variable metadata dict or None if not found
    """
    try:
        response = variables_metadata_table.get_item(
            Key={
                'PK': f"VAR#{variable_id}",
                'SK': 'METADATA'
            }
        )
        
        return response.get('Item')
    except ClientError as e:
        logger.error(f"Error retrieving variable metadata: {e}")
        return None


def query_dynamodb_data(
    variable_id: str,
    area: str,
    start_dt: datetime,
    end_dt: datetime
) -> List[Dict[str, Any]]:
    """
    Query sensor data from DynamoDB for the specified time range.
    
    Uses the partition key (PK = "{area}#{variable_id}") and sort key
    (SK = "DATA#{timestamp_ms}") for efficient range queries.
    
    Args:
        variable_id: Variable ID
        area: Area (pre-treatment, e-coat, production-control)
        start_dt: Start datetime (inclusive)
        end_dt: End datetime (inclusive)
        
    Returns:
        List of data points sorted by timestamp
    """
    # Convert datetimes to milliseconds for SK range query
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    # Build partition key
    pk = f"{area}#{variable_id}"
    
    # Build sort key range
    sk_start = f"DATA#{start_ms}"
    sk_end = f"DATA#{end_ms}"
    
    logger.info(f"Querying DynamoDB: PK={pk}, SK between {sk_start} and {sk_end}")
    
    try:
        # Query with KeyConditionExpression
        response = sensor_data_table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :sk_start AND :sk_end',
            ExpressionAttributeValues={
                ':pk': pk,
                ':sk_start': sk_start,
                ':sk_end': sk_end
            },
            ScanIndexForward=True  # Sort ascending by SK (timestamp)
        )
        
        items = response.get('Items', [])
        
        # Handle pagination if there are many results
        while 'LastEvaluatedKey' in response:
            response = sensor_data_table.query(
                KeyConditionExpression='PK = :pk AND SK BETWEEN :sk_start AND :sk_end',
                ExpressionAttributeValues={
                    ':pk': pk,
                    ':sk_start': sk_start,
                    ':sk_end': sk_end
                },
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ScanIndexForward=True
            )
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} data points from DynamoDB")
        
        return items
        
    except ClientError as e:
        logger.error(f"DynamoDB query error: {e}")
        raise


def query_s3_data(
    variable_id: str,
    area: str,
    start_dt: datetime,
    end_dt: datetime
) -> List[Dict[str, Any]]:
    """
    Query archived sensor data from S3 for the specified time range.
    
    S3 structure: s3://bucket/raw-data/year=YYYY/month=MM/day=DD/area={area}/data.parquet.gz
    
    Args:
        variable_id: Variable ID
        area: Area (pre-treatment, e-coat, production-control)
        start_dt: Start datetime (inclusive)
        end_dt: End datetime (inclusive)
        
    Returns:
        List of data points sorted by timestamp
    """
    if not ARCHIVE_BUCKET:
        logger.warning("Archive bucket not configured, skipping S3 query")
        return []
    
    logger.info(f"Querying S3 archive for variable {variable_id} from {start_dt} to {end_dt}")
    
    # TODO: Implement S3 query using Athena or direct Parquet reading
    # For MVP, we'll return empty list since DynamoDB has 30-day retention
    # which should be sufficient for the prototype
    
    logger.info("S3 archive query not yet implemented (MVP uses DynamoDB only)")
    return []


def format_data_points(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format DynamoDB items to API response format.
    
    Args:
        items: List of DynamoDB items
        
    Returns:
        List of formatted data points
    """
    data_points = []
    
    for item in items:
        data_point = {
            'timestamp': item.get('timestamp'),
            'value': float(item.get('value', 0)),
            'unit': item.get('unit', ''),
            'quality': item.get('quality', 'good')
        }
        
        # Include metadata if present
        if 'metadata' in item:
            data_point['metadata'] = item['metadata']
        
        data_points.append(data_point)
    
    return data_points


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET /variables/{id}/data request.
    
    Retrieves historical sensor data for a specific variable within a time range.
    Query parameters:
    - start: ISO 8601 timestamp (required)
    - end: ISO 8601 timestamp (required)
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with historical data
    """
    request_id = context.request_id if context else 'local'
    
    logger.info(f"Processing GET /variables/{{id}}/data request", extra={
        'request_id': request_id,
        'event': event
    })
    
    try:
        # Step 1: Validate and extract query parameters
        variable_id, start_dt, end_dt = validate_query_params(event)
        
        logger.info(f"Query parameters: variable_id={variable_id}, start={start_dt}, end={end_dt}")
        
        # Step 2: Get variable metadata to determine area
        variable_metadata = get_variable_metadata(variable_id)
        
        if not variable_metadata:
            logger.warning(f"Variable not found: {variable_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': f'Variable {variable_id} no encontrada'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        area = variable_metadata.get('area')
        if not area:
            logger.error(f"Variable {variable_id} has no area defined")
            raise Exception("Variable metadata incomplete")
        
        # Step 3: Query DynamoDB for recent data
        dynamodb_data = query_dynamodb_data(variable_id, area, start_dt, end_dt)
        
        # Step 4: If no data in DynamoDB, try S3 archive (for older data)
        s3_data = []
        if not dynamodb_data:
            logger.info("No data found in DynamoDB, checking S3 archive")
            s3_data = query_s3_data(variable_id, area, start_dt, end_dt)
        
        # Step 5: Combine and format data
        all_data = dynamodb_data + s3_data
        
        # Sort by timestamp (should already be sorted, but ensure it)
        all_data.sort(key=lambda x: x.get('timestamp', ''))
        
        # Format data points
        formatted_data = format_data_points(all_data)
        
        logger.info(f"Returning {len(formatted_data)} data points for variable {variable_id}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': {
                    'variable_id': variable_id,
                    'area': area,
                    'start': start_dt.isoformat().replace('+00:00', 'Z'),
                    'end': end_dt.isoformat().replace('+00:00', 'Z'),
                    'count': len(formatted_data),
                    'data_points': formatted_data,
                    'sources': {
                        'dynamodb': len(dynamodb_data),
                        's3': len(s3_data)
                    }
                },
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'request_id': request_id
            }, default=str)
        }
        
    except ValidationError as e:
        logger.warning(f"Validation error: {e}", extra={'request_id': request_id})
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': str(e)
                },
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'request_id': request_id
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        logger.error(f"DynamoDB error: {error_code}", extra={
            'error': str(e),
            'request_id': request_id
        })
        
        return {
            'statusCode': 503,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'SERVICE_UNAVAILABLE',
                    'message': 'El servicio de base de datos no está disponible temporalmente'
                },
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'request_id': request_id
            })
        }
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}", extra={
            'request_id': request_id
        })
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': False,
                'error': {
                    'code': 'INTERNAL_ERROR',
                    'message': 'Ocurrió un error inesperado al procesar la solicitud'
                },
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'request_id': request_id
            })
        }
