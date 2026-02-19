"""
Lambda handler for GET /statistics/{variable_id} endpoint.

This handler retrieves aggregated statistics for a specific variable
over the last 24 hours. Statistics are pre-calculated by the statistics
Lambda and stored in the statistics DynamoDB table.

Requirements: 5.5
"""

import json
import logging
import os
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
statistics_table_name = os.environ.get('STATISTICS_TABLE', 'kia-paintshop-statistics')
variables_metadata_table_name = os.environ.get('VARIABLES_METADATA_TABLE', 'kia-paintshop-variables-metadata')

statistics_table = dynamodb.Table(statistics_table_name)
variables_metadata_table = dynamodb.Table(variables_metadata_table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET /statistics/{variable_id} request.
    
    Returns aggregated statistics for a variable over the last 24 hours.
    
    Path parameters:
    - variable_id: Variable ID (required)
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with statistics
    """
    request_id = context.request_id if context else 'local'
    
    logger.info(f"Processing GET /statistics/{{variable_id}} request", extra={
        'request_id': request_id
    })
    
    try:
        # Extract variable_id from path parameters
        path_params = event.get('pathParameters', {})
        variable_id = path_params.get('variable_id') if path_params else None
        
        if not variable_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                    'Access-Control-Allow-Methods': 'GET,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'ID de variable requerido en la ruta'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        # Verify variable exists
        logger.info(f"Verifying variable exists: {variable_id}")
        
        try:
            var_response = variables_metadata_table.get_item(
                Key={
                    'PK': f"VAR#{variable_id}",
                    'SK': 'METADATA'
                }
            )
        except ClientError as e:
            logger.error(f"DynamoDB get_item error: {e}")
            raise
        
        if 'Item' not in var_response:
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
        
        variable_metadata = var_response['Item']
        
        # Query statistics for last 24 hours
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(hours=24)
        
        # Format timestamps for query
        start_str = start_time.isoformat().replace('+00:00', 'Z')
        
        logger.info(f"Querying statistics for {variable_id} since {start_str}")
        
        try:
            # Query statistics table
            # PK = variable_id, SK = "STATS#{window_start}"
            response = statistics_table.query(
                KeyConditionExpression='PK = :pk AND SK >= :sk',
                ExpressionAttributeValues={
                    ':pk': variable_id,
                    ':sk': f"STATS#{start_str}"
                },
                ScanIndexForward=False  # Most recent first
            )
        except ClientError as e:
            logger.error(f"DynamoDB query error: {e}")
            raise
        
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            response = statistics_table.query(
                KeyConditionExpression='PK = :pk AND SK >= :sk',
                ExpressionAttributeValues={
                    ':pk': variable_id,
                    ':sk': f"STATS#{start_str}"
                },
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ScanIndexForward=False
            )
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} statistics windows for {variable_id}")
        
        # Format statistics
        statistics_windows = []
        for item in items:
            stat = {
                'window_start': item.get('window_start'),
                'window_end': item.get('window_end'),
                'window_minutes': int(item.get('window_minutes', 0)),
                'count': int(item.get('count', 0)),
                'avg': float(item.get('avg', 0)),
                'min': float(item.get('min', 0)),
                'max': float(item.get('max', 0)),
                'stddev': float(item.get('stddev', 0))
            }
            statistics_windows.append(stat)
        
        # Calculate overall statistics from all windows
        overall_stats = None
        if statistics_windows:
            all_avgs = [s['avg'] for s in statistics_windows]
            all_mins = [s['min'] for s in statistics_windows]
            all_maxs = [s['max'] for s in statistics_windows]
            total_count = sum(s['count'] for s in statistics_windows)
            
            overall_stats = {
                'avg': sum(all_avgs) / len(all_avgs) if all_avgs else 0,
                'min': min(all_mins) if all_mins else 0,
                'max': max(all_maxs) if all_maxs else 0,
                'total_samples': total_count,
                'windows_count': len(statistics_windows)
            }
        
        logger.info(f"Returning {len(statistics_windows)} statistics windows", extra={
            'variable_id': variable_id,
            'windows_count': len(statistics_windows),
            'request_id': request_id
        })
        
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
                    'variable_name': variable_metadata.get('name', ''),
                    'unit': variable_metadata.get('unit', ''),
                    'time_range': {
                        'start': start_str,
                        'end': now.isoformat().replace('+00:00', 'Z'),
                        'hours': 24
                    },
                    'overall': overall_stats,
                    'windows': statistics_windows
                },
                'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                'request_id': request_id
            }, default=str)
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
