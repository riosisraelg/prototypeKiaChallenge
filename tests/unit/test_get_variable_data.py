"""
Unit tests for GET /variables/{id}/data Lambda handler.

Tests cover:
- Query parameter validation
- ISO 8601 timestamp parsing
- DynamoDB query construction
- Variable metadata lookup
- Error handling (validation, not found, service errors)
- Response formatting
"""

import json
import pytest
from datetime import datetime, timezone, timedelta
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal

# Mock boto3 before importing handler
import sys
sys.path.insert(0, 'lambdas/api')

with patch('boto3.resource'), patch('boto3.client'):
    from get_variable_data import (
        handler,
        parse_iso8601_timestamp,
        validate_query_params,
        get_variable_metadata,
        query_dynamodb_data,
        format_data_points,
        ValidationError
    )


class TestTimestampParsing:
    """Test ISO 8601 timestamp parsing."""
    
    def test_parse_iso8601_with_z_suffix(self):
        """Should parse ISO 8601 timestamp with Z suffix."""
        timestamp_str = "2024-01-15T10:30:00Z"
        dt = parse_iso8601_timestamp(timestamp_str)
        
        assert dt.year == 2024
        assert dt.month == 1
        assert dt.day == 15
        assert dt.hour == 10
        assert dt.minute == 30
        assert dt.second == 0
        assert dt.tzinfo == timezone.utc
    
    def test_parse_iso8601_with_timezone(self):
        """Should parse ISO 8601 timestamp with timezone offset."""
        timestamp_str = "2024-01-15T10:30:00+00:00"
        dt = parse_iso8601_timestamp(timestamp_str)
        
        assert dt.year == 2024
        assert dt.tzinfo is not None
    
    def test_parse_iso8601_invalid_format(self):
        """Should raise ValidationError for invalid timestamp format."""
        with pytest.raises(ValidationError) as exc_info:
            parse_iso8601_timestamp("invalid-timestamp")
        
        assert "Formato de timestamp inválido" in str(exc_info.value)
    
    def test_parse_iso8601_empty_string(self):
        """Should raise ValidationError for empty string."""
        with pytest.raises(ValidationError):
            parse_iso8601_timestamp("")


class TestQueryParamsValidation:
    """Test query parameter validation."""
    
    def test_validate_query_params_success(self):
        """Should successfully validate valid query parameters."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        variable_id, start_dt, end_dt = validate_query_params(event)
        
        assert variable_id == 'PT-TEMP-001'
        assert start_dt < end_dt
        assert (end_dt - start_dt).total_seconds() == 3600  # 1 hour
    
    def test_validate_query_params_missing_path_params(self):
        """Should raise ValidationError when path parameters are missing."""
        event = {
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "ID de variable requerido" in str(exc_info.value)
    
    def test_validate_query_params_missing_variable_id(self):
        """Should raise ValidationError when variable ID is missing."""
        event = {
            'pathParameters': {},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "ID de variable requerido" in str(exc_info.value)
    
    def test_validate_query_params_missing_start(self):
        """Should raise ValidationError when start parameter is missing."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "start" in str(exc_info.value).lower()
    
    def test_validate_query_params_missing_end(self):
        """Should raise ValidationError when end parameter is missing."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "end" in str(exc_info.value).lower()
    
    def test_validate_query_params_start_after_end(self):
        """Should raise ValidationError when start is after end."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T11:00:00Z',
                'end': '2024-01-15T10:00:00Z'
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "anterior" in str(exc_info.value)
    
    def test_validate_query_params_range_too_large(self):
        """Should raise ValidationError when time range exceeds 7 days."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-01T00:00:00Z',
                'end': '2024-01-10T00:00:00Z'  # 9 days
            }
        }
        
        with pytest.raises(ValidationError) as exc_info:
            validate_query_params(event)
        
        assert "7 días" in str(exc_info.value)


class TestDataFormatting:
    """Test data point formatting."""
    
    def test_format_data_points_basic(self):
        """Should format basic data points correctly."""
        items = [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'value': Decimal('65.5'),
                'unit': '°C',
                'quality': 'good'
            },
            {
                'timestamp': '2024-01-15T10:05:00Z',
                'value': Decimal('66.0'),
                'unit': '°C',
                'quality': 'good'
            }
        ]
        
        formatted = format_data_points(items)
        
        assert len(formatted) == 2
        assert formatted[0]['timestamp'] == '2024-01-15T10:00:00Z'
        assert formatted[0]['value'] == 65.5
        assert formatted[0]['unit'] == '°C'
        assert formatted[0]['quality'] == 'good'
    
    def test_format_data_points_with_metadata(self):
        """Should include metadata when present."""
        items = [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'value': Decimal('65.5'),
                'unit': '°C',
                'quality': 'good',
                'metadata': {
                    'min_range': 60.0,
                    'max_range': 70.0
                }
            }
        ]
        
        formatted = format_data_points(items)
        
        assert 'metadata' in formatted[0]
        assert formatted[0]['metadata']['min_range'] == 60.0
    
    def test_format_data_points_empty_list(self):
        """Should handle empty list."""
        formatted = format_data_points([])
        assert formatted == []


class TestHandler:
    """Test main Lambda handler."""
    
    @patch('get_variable_data.query_dynamodb_data')
    @patch('get_variable_data.get_variable_metadata')
    def test_handler_success(self, mock_get_metadata, mock_query_dynamodb):
        """Should successfully retrieve and return data."""
        # Setup mocks
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'name': 'Temperature Tank 1'
        }
        
        mock_query_dynamodb.return_value = [
            {
                'timestamp': '2024-01-15T10:00:00Z',
                'value': Decimal('65.5'),
                'unit': '°C',
                'quality': 'good'
            },
            {
                'timestamp': '2024-01-15T10:05:00Z',
                'value': Decimal('66.0'),
                'unit': '°C',
                'quality': 'good'
            }
        ]
        
        # Create event
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        # Create context
        context = Mock()
        context.request_id = 'test-request-id'
        
        # Call handler
        response = handler(event, context)
        
        # Verify response
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['variable_id'] == 'PT-TEMP-001'
        assert body['data']['area'] == 'pre-treatment'
        assert body['data']['count'] == 2
        assert len(body['data']['data_points']) == 2
        assert body['data']['data_points'][0]['value'] == 65.5
    
    @patch('get_variable_data.get_variable_metadata')
    def test_handler_variable_not_found(self, mock_get_metadata):
        """Should return 404 when variable is not found."""
        mock_get_metadata.return_value = None
        
        event = {
            'pathParameters': {'id': 'INVALID-VAR'},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-id'
        
        response = handler(event, context)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'NOT_FOUND'
    
    def test_handler_validation_error(self):
        """Should return 400 for validation errors."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T11:00:00Z',
                'end': '2024-01-15T10:00:00Z'  # End before start
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-id'
        
        response = handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'VALIDATION_ERROR'
    
    def test_handler_missing_query_params(self):
        """Should return 400 when query parameters are missing."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': None
        }
        
        context = Mock()
        context.request_id = 'test-request-id'
        
        response = handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
    
    @patch('get_variable_data.query_dynamodb_data')
    @patch('get_variable_data.get_variable_metadata')
    def test_handler_empty_results(self, mock_get_metadata, mock_query_dynamodb):
        """Should return empty data when no results found."""
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment'
        }
        
        mock_query_dynamodb.return_value = []
        
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': '2024-01-15T10:00:00Z',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-id'
        
        response = handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['count'] == 0
        assert body['data']['data_points'] == []
    
    def test_handler_cors_headers(self):
        """Should include CORS headers in response."""
        event = {
            'pathParameters': {'id': 'PT-TEMP-001'},
            'queryStringParameters': {
                'start': 'invalid',
                'end': '2024-01-15T11:00:00Z'
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-id'
        
        response = handler(event, context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
