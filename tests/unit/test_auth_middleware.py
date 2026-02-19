"""
Unit tests for authentication middleware.

Tests API key validation and authentication decorator.
"""

import json
import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_context():
    """Mock Lambda context."""
    context = MagicMock()
    context.request_id = 'test-request-123'
    return context


@pytest.fixture
def valid_api_event():
    """Event with valid API key."""
    return {
        'httpMethod': 'GET',
        'path': '/test',
        'headers': {
            'x-api-key': 'test-api-key-12345'
        }
    }


@pytest.fixture
def invalid_api_event():
    """Event with invalid API key."""
    return {
        'httpMethod': 'GET',
        'path': '/test',
        'headers': {
            'x-api-key': 'wrong-key'
        }
    }


@pytest.fixture
def missing_api_key_event():
    """Event without API key."""
    return {
        'httpMethod': 'GET',
        'path': '/test',
        'headers': {}
    }


def test_validate_api_key_success():
    """Test successful API key validation."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import validate_api_key
        
        event = {
            'headers': {
                'x-api-key': 'test-api-key-12345'
            }
        }
        
        is_valid, error_message = validate_api_key(event)
        
        assert is_valid is True
        assert error_message is None


def test_validate_api_key_case_insensitive():
    """Test that header name is case-insensitive."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import validate_api_key
        
        event = {
            'headers': {
                'X-Api-Key': 'test-api-key-12345'  # Different case
            }
        }
        
        is_valid, error_message = validate_api_key(event)
        
        assert is_valid is True
        assert error_message is None


def test_validate_api_key_invalid():
    """Test validation with invalid API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import validate_api_key
        
        event = {
            'headers': {
                'x-api-key': 'wrong-key'
            }
        }
        
        is_valid, error_message = validate_api_key(event)
        
        assert is_valid is False
        assert 'inválida' in error_message


def test_validate_api_key_missing():
    """Test validation with missing API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import validate_api_key
        
        event = {
            'headers': {}
        }
        
        is_valid, error_message = validate_api_key(event)
        
        assert is_valid is False
        assert 'requerida' in error_message


def test_validate_api_key_no_env_configured():
    """Test validation when API_KEY environment variable is not set."""
    # Patch the API_KEY variable directly in the module
    with patch('lambdas.api.auth_middleware.API_KEY', ''):
        from lambdas.api.auth_middleware import validate_api_key
        
        event = {
            'headers': {
                'x-api-key': 'some-key'
            }
        }
        
        is_valid, error_message = validate_api_key(event)
        
        assert is_valid is False
        assert 'configuración' in error_message.lower()


def test_create_unauthorized_response():
    """Test creation of unauthorized response."""
    from lambdas.api.auth_middleware import create_unauthorized_response
    
    response = create_unauthorized_response('Test error', 'test-request-id')
    
    assert response['statusCode'] == 401
    assert 'Access-Control-Allow-Origin' in response['headers']
    
    body = json.loads(response['body'])
    assert body['success'] is False
    assert body['error']['code'] == 'UNAUTHORIZED'
    assert body['error']['message'] == 'Test error'
    assert body['request_id'] == 'test-request-id'


def test_require_auth_decorator_success(mock_context):
    """Test require_auth decorator with valid API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import require_auth
        
        @require_auth
        def test_handler(event, context):
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'success'})
            }
        
        event = {
            'headers': {
                'x-api-key': 'test-api-key-12345'
            }
        }
        
        response = test_handler(event, mock_context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['message'] == 'success'


def test_require_auth_decorator_invalid_key(mock_context):
    """Test require_auth decorator with invalid API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import require_auth
        
        @require_auth
        def test_handler(event, context):
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'success'})
            }
        
        event = {
            'headers': {
                'x-api-key': 'wrong-key'
            }
        }
        
        response = test_handler(event, mock_context)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'UNAUTHORIZED'


def test_require_auth_decorator_missing_key(mock_context):
    """Test require_auth decorator with missing API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import require_auth
        
        @require_auth
        def test_handler(event, context):
            return {
                'statusCode': 200,
                'body': json.dumps({'message': 'success'})
            }
        
        event = {
            'headers': {}
        }
        
        response = test_handler(event, mock_context)
        
        assert response['statusCode'] == 401
        body = json.loads(response['body'])
        assert body['success'] is False


def test_check_auth_success(mock_context):
    """Test check_auth function with valid API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import check_auth
        
        event = {
            'headers': {
                'x-api-key': 'test-api-key-12345'
            }
        }
        
        result = check_auth(event, mock_context)
        
        assert result is None  # No error response


def test_check_auth_failure(mock_context):
    """Test check_auth function with invalid API key."""
    with patch.dict(os.environ, {'API_KEY': 'test-api-key-12345'}):
        from lambdas.api.auth_middleware import check_auth
        
        event = {
            'headers': {
                'x-api-key': 'wrong-key'
            }
        }
        
        result = check_auth(event, mock_context)
        
        assert result is not None
        assert result['statusCode'] == 401


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
