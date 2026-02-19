"""
Lambda handler for GET /alarms endpoint.

This handler retrieves alarms from the alarms DynamoDB table, optionally
filtered by status (active, acknowledged, resolved).

The alarms table uses:
- PK = "ALARM#{alarm_id}"
- SK = "METADATA"
- GSI1: status (PK) + created_at (SK) for filtering by status

Requirements: 5.3
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

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('ALARMS_TABLE', 'kia-paintshop-alarms')
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET /alarms request.
    
    Returns list of alarms, optionally filtered by status.
    Query parameters:
    - status: Filter by alarm status (active, acknowledged, resolved) - optional
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with alarms list
    """
    request_id = context.request_id if context else 'local'
    
    logger.info(f"Processing GET /alarms request", extra={
        'request_id': request_id
    })
    
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters', {}) or {}
        status_filter = query_params.get('status')
        
        # Validate status filter if provided
        valid_statuses = ['active', 'acknowledged', 'resolved']
        if status_filter and status_filter not in valid_statuses:
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
                        'message': f'Estado inválido. Debe ser uno de: {", ".join(valid_statuses)}'
                    },
                    'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                    'request_id': request_id
                })
            }
        
        # Query alarms
        if status_filter:
            # Use GSI to filter by status
            logger.info(f"Querying alarms with status: {status_filter}")
            response = table.query(
                IndexName='status-created_at-index',
                KeyConditionExpression='#status = :status',
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': status_filter
                },
                ScanIndexForward=False  # Sort descending by created_at
            )
        else:
            # Scan all alarms
            logger.info("Scanning all alarms")
            response = table.scan()
        
        items = response.get('Items', [])
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            if status_filter:
                response = table.query(
                    IndexName='status-created_at-index',
                    KeyConditionExpression='#status = :status',
                    ExpressionAttributeNames={
                        '#status': 'status'
                    },
                    ExpressionAttributeValues={
                        ':status': status_filter
                    },
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    ScanIndexForward=False
                )
            else:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} alarms")
        
        # Transform DynamoDB items to API response format
        alarms = []
        for item in items:
            # Skip items that don't have the METADATA sort key
            if item.get('SK') != 'METADATA':
                continue
            
            alarm = {
                'alarm_id': item.get('alarm_id'),
                'variable_id': item.get('variable_id'),
                'area': item.get('area'),
                'severity': item.get('severity'),
                'status': item.get('status'),
                'message': item.get('message', ''),
                'value': float(item.get('value', 0)),
                'threshold': float(item.get('threshold', 0)),
                'created_at': item.get('created_at'),
                'acknowledged_at': item.get('acknowledged_at'),
                'resolved_at': item.get('resolved_at'),
                'acknowledged_by': item.get('acknowledged_by')
            }
            alarms.append(alarm)
        
        # Sort by created_at descending (most recent first)
        alarms.sort(key=lambda x: x['created_at'], reverse=True)
        
        # Calculate summary statistics
        summary = {
            'total': len(alarms),
            'by_status': {
                'active': sum(1 for a in alarms if a['status'] == 'active'),
                'acknowledged': sum(1 for a in alarms if a['status'] == 'acknowledged'),
                'resolved': sum(1 for a in alarms if a['status'] == 'resolved')
            },
            'by_severity': {
                'warning': sum(1 for a in alarms if a['severity'] == 'warning'),
                'critical': sum(1 for a in alarms if a['severity'] == 'critical')
            }
        }
        
        logger.info(f"Returning {len(alarms)} alarms", extra={
            'summary': summary,
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
                    'alarms': alarms,
                    'summary': summary,
                    'filter': {
                        'status': status_filter
                    }
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
