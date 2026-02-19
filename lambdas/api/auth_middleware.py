"""
Authentication middleware for API Lambda handlers.

This module provides authentication validation using API keys.
The API key is expected in the 'x-api-key' header.

Requirements: 5.6, 10.2
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Callable

# Configure logging
logger = logging.getLogger()
logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))

# Get API key from environment
API_KEY = os.environ.get('API_KEY', '')


def validate_api_key(event: Dict[str, Any]) -> tuple[bool, Optional[str]]:
    """
    Validate API key from request headers.
    
    Args:
        event: API Gateway event
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Extract headers (case-insensitive)
    headers = event.get('headers', {})
    
    # API Gateway may lowercase headers
    api_key = headers.get('x-api-key') or headers.get('X-Api-Key')
    
    if not API_KEY:
        logger.error("API_KEY environment variable not configured")
        return False, "Configuración de autenticación no disponible"
    
    if not api_key:
        logger.warning("Missing API key in request headers")
        return False, "API key requerida en header 'x-api-key'"
    
    if api_key != API_KEY:
        logger.warning("Invalid API key provided", extra={
            'provided_key_prefix': api_key[:8] if len(api_key) >= 8 else api_key
        })
        return False, "API key inválida"
    
    return True, None


def create_unauthorized_response(error_message: str, request_id: str = 'unknown') -> Dict[str, Any]:
    """
    Create a standardized 401 Unauthorized response.
    
    Args:
        error_message: Error message to include
        request_id: Request ID for tracking
        
    Returns:
        API Gateway response dict
    """
    return {
        'statusCode': 401,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Api-Key',
            'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
        },
        'body': json.dumps({
            'success': False,
            'error': {
                'code': 'UNAUTHORIZED',
                'message': error_message
            },
            'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            'request_id': request_id
        })
    }


def require_auth(handler: Callable) -> Callable:
    """
    Decorator to require authentication for a Lambda handler.
    
    Usage:
        @require_auth
        def handler(event, context):
            # Handler code
            pass
    
    Args:
        handler: Lambda handler function
        
    Returns:
        Wrapped handler function
    """
    def wrapper(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
        request_id = context.request_id if context else 'unknown'
        
        # Validate API key
        is_valid, error_message = validate_api_key(event)
        
        if not is_valid:
            logger.warning(f"Authentication failed: {error_message}", extra={
                'request_id': request_id,
                'path': event.get('path', 'unknown')
            })
            return create_unauthorized_response(error_message, request_id)
        
        # Authentication successful, call original handler
        logger.info("Authentication successful", extra={
            'request_id': request_id
        })
        
        return handler(event, context)
    
    return wrapper


def check_auth(event: Dict[str, Any], context: Any) -> Optional[Dict[str, Any]]:
    """
    Check authentication and return error response if invalid.
    
    This is an alternative to the decorator for handlers that need
    more control over the authentication flow.
    
    Args:
        event: API Gateway event
        context: Lambda context
        
    Returns:
        Error response dict if authentication fails, None if successful
    """
    request_id = context.request_id if context else 'unknown'
    
    is_valid, error_message = validate_api_key(event)
    
    if not is_valid:
        logger.warning(f"Authentication failed: {error_message}", extra={
            'request_id': request_id,
            'path': event.get('path', 'unknown')
        })
        return create_unauthorized_response(error_message, request_id)
    
    logger.info("Authentication successful", extra={
        'request_id': request_id
    })
    
    return None
