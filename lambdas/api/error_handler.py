"""
Error handling utilities for API Lambda handlers.

Provides consistent error response formatting and logging.

Requirements: 5.7
"""

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Configure logging
logger = logging.getLogger()


class APIError(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, code: str = 'API_ERROR', status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class ValidationError(APIError):
    """Validation error (400)."""
    
    def __init__(self, message: str):
        super().__init__(message, code='VALIDATION_ERROR', status_code=400)


class NotFoundError(APIError):
    """Resource not found error (404)."""
    
    def __init__(self, message: str):
        super().__init__(message, code='NOT_FOUND', status_code=404)


class UnauthorizedError(APIError):
    """Unauthorized error (401)."""
    
    def __init__(self, message: str):
        super().__init__(message, code='UNAUTHORIZED', status_code=401)


class ServiceUnavailableError(APIError):
    """Service unavailable error (503)."""
    
    def __init__(self, message: str):
        super().__init__(message, code='SERVICE_UNAVAILABLE', status_code=503)


def create_error_response(
    error_code: str,
    error_message: str,
    status_code: int = 500,
    request_id: str = 'unknown',
    additional_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        error_code: Error code (e.g., 'VALIDATION_ERROR', 'NOT_FOUND')
        error_message: Human-readable error message
        status_code: HTTP status code
        request_id: Request ID for tracking
        additional_data: Optional additional data to include in response
        
    Returns:
        API Gateway response dict
    """
    body = {
        'success': False,
        'error': {
            'code': error_code,
            'message': error_message
        },
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'request_id': request_id
    }
    
    if additional_data:
        body.update(additional_data)
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body)
    }


def create_success_response(
    data: Any,
    status_code: int = 200,
    request_id: str = 'unknown',
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized success response.
    
    Args:
        data: Response data
        status_code: HTTP status code
        request_id: Request ID for tracking
        message: Optional success message
        
    Returns:
        API Gateway response dict
    """
    body = {
        'success': True,
        'data': data,
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'request_id': request_id
    }
    
    if message:
        body['message'] = message
    
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps(body, default=str)
    }


def handle_error(error: Exception, request_id: str = 'unknown') -> Dict[str, Any]:
    """
    Handle an exception and return appropriate error response.
    
    Args:
        error: Exception to handle
        request_id: Request ID for tracking
        
    Returns:
        API Gateway error response dict
    """
    # Handle known API errors
    if isinstance(error, APIError):
        logger.warning(f"{error.code}: {error.message}", extra={
            'request_id': request_id,
            'error_code': error.code
        })
        return create_error_response(
            error_code=error.code,
            error_message=error.message,
            status_code=error.status_code,
            request_id=request_id
        )
    
    # Handle DynamoDB errors
    if hasattr(error, 'response') and 'Error' in error.response:
        error_code = error.response['Error']['Code']
        
        logger.error(f"DynamoDB error: {error_code}", extra={
            'request_id': request_id,
            'error': str(error)
        })
        
        # Map DynamoDB errors to appropriate HTTP status codes
        if error_code in ['ProvisionedThroughputExceededException', 'RequestLimitExceeded']:
            return create_error_response(
                error_code='SERVICE_UNAVAILABLE',
                error_message='El servicio de base de datos no está disponible temporalmente',
                status_code=503,
                request_id=request_id
            )
        elif error_code == 'ResourceNotFoundException':
            return create_error_response(
                error_code='NOT_FOUND',
                error_message='Recurso no encontrado',
                status_code=404,
                request_id=request_id
            )
        else:
            return create_error_response(
                error_code='DATABASE_ERROR',
                error_message='Error al acceder a la base de datos',
                status_code=500,
                request_id=request_id
            )
    
    # Handle unexpected errors
    logger.exception(f"Unexpected error: {error}", extra={
        'request_id': request_id
    })
    
    return create_error_response(
        error_code='INTERNAL_ERROR',
        error_message='Ocurrió un error inesperado al procesar la solicitud',
        status_code=500,
        request_id=request_id
    )


def log_error(
    error: Exception,
    context: Dict[str, Any],
    request_id: str = 'unknown'
) -> None:
    """
    Log an error with structured context.
    
    Args:
        error: Exception to log
        context: Additional context information
        request_id: Request ID for tracking
    """
    error_info = {
        'request_id': request_id,
        'error_type': type(error).__name__,
        'error_message': str(error),
        'context': context
    }
    
    if isinstance(error, APIError):
        error_info['error_code'] = error.code
        error_info['status_code'] = error.status_code
    
    logger.error(f"Error occurred: {error}", extra=error_info)
