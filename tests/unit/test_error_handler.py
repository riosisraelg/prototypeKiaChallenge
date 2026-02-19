"""
Unit tests for error handler utilities.

Tests error response formatting and exception handling.
"""

import json
from datetime import datetime
from unittest.mock import MagicMock

import pytest


def test_create_error_response():
    """Test creation of error response."""
    from lambdas.api.error_handler import create_error_response
    
    response = create_error_response(
        error_code='TEST_ERROR',
        error_message='Test error message',
        status_code=400,
        request_id='test-request-123'
    )
    
    assert response['statusCode'] == 400
    assert 'Access-Control-Allow-Origin' in response['headers']
    
    body = json.loads(response['body'])
    assert body['success'] is False
    assert body['error']['code'] == 'TEST_ERROR'
    assert body['error']['message'] == 'Test error message'
    assert body['request_id'] == 'test-request-123'
    assert 'timestamp' in body


def test_create_error_response_with_additional_data():
    """Test error response with additional data."""
    from lambdas.api.error_handler import create_error_response
    
    response = create_error_response(
        error_code='TEST_ERROR',
        error_message='Test error',
        status_code=400,
        request_id='test-request-123',
        additional_data={'details': 'Extra information'}
    )
    
    body = json.loads(response['body'])
    assert body['details'] == 'Extra information'


def test_create_success_response():
    """Test creation of success response."""
    from lambdas.api.error_handler import create_success_response
    
    response = create_success_response(
        data={'result': 'success'},
        status_code=200,
        request_id='test-request-123'
    )
    
    assert response['statusCode'] == 200
    
    body = json.loads(response['body'])
    assert body['success'] is True
    assert body['data']['result'] == 'success'
    assert body['request_id'] == 'test-request-123'
    assert 'timestamp' in body


def test_create_success_response_with_message():
    """Test success response with message."""
    from lambdas.api.error_handler import create_success_response
    
    response = create_success_response(
        data={'result': 'success'},
        message='Operation completed successfully',
        request_id='test-request-123'
    )
    
    body = json.loads(response['body'])
    assert body['message'] == 'Operation completed successfully'


def test_validation_error():
    """Test ValidationError exception."""
    from lambdas.api.error_handler import ValidationError
    
    error = ValidationError('Invalid input')
    
    assert error.message == 'Invalid input'
    assert error.code == 'VALIDATION_ERROR'
    assert error.status_code == 400


def test_not_found_error():
    """Test NotFoundError exception."""
    from lambdas.api.error_handler import NotFoundError
    
    error = NotFoundError('Resource not found')
    
    assert error.message == 'Resource not found'
    assert error.code == 'NOT_FOUND'
    assert error.status_code == 404


def test_unauthorized_error():
    """Test UnauthorizedError exception."""
    from lambdas.api.error_handler import UnauthorizedError
    
    error = UnauthorizedError('Unauthorized access')
    
    assert error.message == 'Unauthorized access'
    assert error.code == 'UNAUTHORIZED'
    assert error.status_code == 401


def test_service_unavailable_error():
    """Test ServiceUnavailableError exception."""
    from lambdas.api.error_handler import ServiceUnavailableError
    
    error = ServiceUnavailableError('Service unavailable')
    
    assert error.message == 'Service unavailable'
    assert error.code == 'SERVICE_UNAVAILABLE'
    assert error.status_code == 503


def test_handle_error_api_error():
    """Test handling of APIError."""
    from lambdas.api.error_handler import handle_error, ValidationError
    
    error = ValidationError('Invalid input')
    response = handle_error(error, 'test-request-123')
    
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert body['error']['code'] == 'VALIDATION_ERROR'
    assert body['error']['message'] == 'Invalid input'


def test_handle_error_dynamodb_throttling():
    """Test handling of DynamoDB throttling error."""
    from lambdas.api.error_handler import handle_error
    from botocore.exceptions import ClientError
    
    error = ClientError(
        {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
        'Query'
    )
    
    response = handle_error(error, 'test-request-123')
    
    assert response['statusCode'] == 503
    body = json.loads(response['body'])
    assert body['error']['code'] == 'SERVICE_UNAVAILABLE'


def test_handle_error_dynamodb_resource_not_found():
    """Test handling of DynamoDB ResourceNotFoundException."""
    from lambdas.api.error_handler import handle_error
    from botocore.exceptions import ClientError
    
    error = ClientError(
        {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Not found'}},
        'GetItem'
    )
    
    response = handle_error(error, 'test-request-123')
    
    assert response['statusCode'] == 404
    body = json.loads(response['body'])
    assert body['error']['code'] == 'NOT_FOUND'


def test_handle_error_unexpected():
    """Test handling of unexpected error."""
    from lambdas.api.error_handler import handle_error
    
    error = Exception('Unexpected error')
    response = handle_error(error, 'test-request-123')
    
    assert response['statusCode'] == 500
    body = json.loads(response['body'])
    assert body['error']['code'] == 'INTERNAL_ERROR'


def test_log_error():
    """Test error logging with context."""
    from lambdas.api.error_handler import log_error, ValidationError
    
    error = ValidationError('Test error')
    context = {'user_id': '123', 'action': 'test'}
    
    # Should not raise exception
    log_error(error, context, 'test-request-123')


def test_api_error_base_class():
    """Test APIError base class."""
    from lambdas.api.error_handler import APIError
    
    error = APIError('Test error', code='TEST_CODE', status_code=418)
    
    assert error.message == 'Test error'
    assert error.code == 'TEST_CODE'
    assert error.status_code == 418
    assert str(error) == 'Test error'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
