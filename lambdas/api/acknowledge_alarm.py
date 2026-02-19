"""
Lambda handler for POST /alarms/{id}/acknowledge endpoint.

This handler updates an alarm's status from 'active' to 'acknowledged',
recording the timestamp and optionally the user who acknowledged it.

Requirements: 5.4
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('ALARMS_TABLE', 'kia-paintshop-alarms')
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle POST /alarms/{id}/acknowledge request.
    
    Updates an alarm's status from 'active' to 'acknowledged'.
    
    Path parameters:
    - id: Alarm ID (required)
    
    Optional body parameters:
    - acknowledged_by: User/operator who acknowledged the alarm
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with updated alarm
    """
    request_id = context.request_id if context else 'local'
    
    logger.info(f"Processing POST /alarms/{{id}}/acknowledge request", extra={
        'request_id': request_id
    })
    
    try:
        # Extract alarm ID from path parameters
        path_params = event.get('pathParameters', {})
        alarm_id = path_params.get('id') if path_params else None
        
        if not alarm_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'VALIDATION_ERROR',
                        'message': 'ID de alarma requerido en la ruta'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        # Parse optional body parameters
        acknowledged_by = None
        if event.get('body'):
            try:
                body = json.loads(event['body'])
                acknowledged_by = body.get('acknowledged_by')
            except json.JSONDecodeError:
                logger.warning("Invalid JSON in request body, ignoring")
        
        # Get current alarm state
        pk = f"ALARM#{alarm_id}"
        sk = "METADATA"
        
        logger.info(f"Retrieving alarm: {alarm_id}")
        
        try:
            response = table.get_item(
                Key={
                    'PK': pk,
                    'SK': sk
                }
            )
        except ClientError as e:
            logger.error(f"DynamoDB get_item error: {e}")
            raise
        
        if 'Item' not in response:
            logger.warning(f"Alarm not found: {alarm_id}")
            return {
                'statusCode': 404,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'NOT_FOUND',
                        'message': f'Alarma {alarm_id} no encontrada'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        alarm = response['Item']
        current_status = alarm.get('status')
        
        # Validate that alarm is in 'active' state
        if current_status != 'active':
            logger.warning(f"Alarm {alarm_id} is not active (status: {current_status})")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({
                    'success': False,
                    'error': {
                        'code': 'INVALID_STATE',
                        'message': f'La alarma debe estar en estado "active" para ser reconocida. Estado actual: {current_status}'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        # Update alarm status to 'acknowledged'
        acknowledged_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        
        update_expression = "SET #status = :status, acknowledged_at = :acknowledged_at"
        expression_attribute_names = {
            '#status': 'status'
        }
        expression_attribute_values = {
            ':status': 'acknowledged',
            ':acknowledged_at': acknowledged_at
        }
        
        # Add acknowledged_by if provided
        if acknowledged_by:
            update_expression += ", acknowledged_by = :acknowledged_by"
            expression_attribute_values[':acknowledged_by'] = acknowledged_by
        
        logger.info(f"Updating alarm {alarm_id} to acknowledged")
        
        try:
            response = table.update_item(
                Key={
                    'PK': pk,
                    'SK': sk
                },
                UpdateExpression=update_expression,
                ExpressionAttributeNames=expression_attribute_names,
                ExpressionAttributeValues=expression_attribute_values,
                ReturnValues='ALL_NEW'
            )
        except ClientError as e:
            logger.error(f"DynamoDB update_item error: {e}")
            raise
        
        updated_alarm = response['Attributes']
        
        # Format response
        alarm_response = {
            'alarm_id': updated_alarm.get('alarm_id'),
            'variable_id': updated_alarm.get('variable_id'),
            'area': updated_alarm.get('area'),
            'severity': updated_alarm.get('severity'),
            'status': updated_alarm.get('status'),
            'message': updated_alarm.get('message', ''),
            'value': float(updated_alarm.get('value', 0)),
            'threshold': float(updated_alarm.get('threshold', 0)),
            'created_at': updated_alarm.get('created_at'),
            'acknowledged_at': updated_alarm.get('acknowledged_at'),
            'acknowledged_by': updated_alarm.get('acknowledged_by'),
            'resolved_at': updated_alarm.get('resolved_at')
        }
        
        logger.info(f"Successfully acknowledged alarm {alarm_id}", extra={
            'alarm_id': alarm_id,
            'acknowledged_at': acknowledged_at,
            'acknowledged_by': acknowledged_by,
            'request_id': request_id
        })
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'success': True,
                'data': {
                    'alarm': alarm_response,
                    'message': 'Alarma reconocida exitosamente'
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
