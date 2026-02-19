"""
Lambda handler for GET /variables endpoint.

This handler retrieves all variables from the variables-metadata DynamoDB table
and returns them organized by area (pre-treatment, e-coat, production-control).

Requirements: 5.1
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('VARIABLES_METADATA_TABLE', 'kia-paintshop-variables-metadata')
table = dynamodb.Table(table_name)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle GET /variables request.
    
    Returns list of all 100 variables with their metadata, organized by area.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        API Gateway response with variables list
    """
    request_id = context.request_id if context else 'local'
    
    logger.info(f"Processing GET /variables request", extra={
        'request_id': request_id
    })
    
    try:
        # Scan the variables-metadata table
        # Note: Scan is acceptable here since we have only ~100 variables
        response = table.scan()
        
        items = response.get('Items', [])
        
        # Handle pagination if needed (unlikely with 100 items)
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        logger.info(f"Retrieved {len(items)} variables from DynamoDB")
        
        # Transform DynamoDB items to API response format
        variables = []
        for item in items:
            # Skip items that don't have the METADATA sort key
            if item.get('SK') != 'METADATA':
                continue
            
            variable = {
                'variable_id': item.get('variable_id'),
                'name': item.get('name'),
                'area': item.get('area'),
                'unit': item.get('unit'),
                'data_type': item.get('data_type', 'float'),
                'min_range': float(item.get('min_range', 0)),
                'max_range': float(item.get('max_range', 0)),
                'alarm_low': float(item.get('alarm_low', 0)),
                'alarm_high': float(item.get('alarm_high', 0)),
                'description': item.get('description', ''),
                'source_file': item.get('source_file', ''),
                'active': item.get('active', True)
            }
            variables.append(variable)
        
        # Organize by area
        organized = {
            'pre-treatment': [],
            'e-coat': [],
            'production-control': []
        }
        
        for var in variables:
            area = var.get('area')
            if area in organized:
                organized[area].append(var)
        
        # Sort variables within each area by variable_id
        for area in organized:
            organized[area].sort(key=lambda x: x['variable_id'])
        
        # Calculate summary statistics
        summary = {
            'total': len(variables),
            'by_area': {
                'pre-treatment': len(organized['pre-treatment']),
                'e-coat': len(organized['e-coat']),
                'production-control': len(organized['production-control'])
            },
            'active': sum(1 for v in variables if v.get('active', True))
        }
        
        logger.info(f"Returning {len(variables)} variables", extra={
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
                    'variables': organized,
                    'summary': summary
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
