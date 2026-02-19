"""
Unit tests for POST /alarms/{id}/acknowledge Lambda handler.

Tests the acknowledge_alarm handler that updates an alarm's status
from 'active' to 'acknowledged'.
"""

import json
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table with sample alarm."""
    table = MagicMock()
    
    # Sample active alarm
    active_alarm = {
        'PK': 'ALARM#alarm-001',
        'SK': 'METADATA',
        'alarm_id': 'alarm-001',
        'variable_id': 'PT-001',
        'area': 'pre-treatment',
        'severity': 'critical',
        'status': 'active',
        'message': 'Temperature exceeds critical threshold',
        'value': Decimal('75.0'),
        'threshold': Decimal('69.0'),
        'created_at': '2024-01-15T10:00:00Z'
    }
    
    # Mock get_item
    table.get_item.return_value = {'Item': active_alarm}
    
    # Mock update_item
    def update_side_effect(*args, **kwargs):
        updated = active_alarm.copy()
        updated['status'] = 'acknowledged'
        updated['acknowledged_at'] = '2024-01-15T10:05:00Z'
        if ':acknowledged_by' in kwargs.get('ExpressionAttributeValues', {}):
            updated['acknowledged_by'] = kwargs['ExpressionAttributeValues'][':acknowledged_by']
        return {'Attributes': updated}
    
    table.update_item.side_effect = update_side_effect
    
    return table


@pytest.fixture
def mock_context():
    """Mock Lambda context."""
    context = MagicMock()
    context.request_id = 'test-request-123'
    return context


@pytest.fixture
def api_event():
    """Sample API Gateway event."""
    return {
        'httpMethod': 'POST',
        'path': '/alarms/alarm-001/acknowledge',
        'pathParameters': {
            'id': 'alarm-001'
        },
        'headers': {
            'x-api-key': 'test-key'
        },
        'body': None
    }


def test_acknowledge_alarm_success(mock_dynamodb_table, mock_context, api_event):
    """Test successful alarm acknowledgment."""
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'alarm' in body['data']
        
        alarm = body['data']['alarm']
        assert alarm['alarm_id'] == 'alarm-001'
        assert alarm['status'] == 'acknowledged'
        assert alarm['acknowledged_at'] is not None


def test_acknowledge_alarm_with_user(mock_dynamodb_table, mock_context, api_event):
    """Test alarm acknowledgment with acknowledged_by field."""
    api_event['body'] = json.dumps({'acknowledged_by': 'operator-1'})
    
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        alarm = body['data']['alarm']
        
        assert alarm['acknowledged_by'] == 'operator-1'


def test_acknowledge_alarm_missing_id(mock_dynamodb_table, mock_context):
    """Test error when alarm ID is missing."""
    event = {
        'httpMethod': 'POST',
        'path': '/alarms/acknowledge',
        'pathParameters': None,
        'headers': {'x-api-key': 'test-key'},
        'body': None
    }
    
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(event, mock_context)
        
        assert response['statusCode'] == 400
        
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'VALIDATION_ERROR'
        assert 'requerido' in body['error']['message']


def test_acknowledge_alarm_not_found(mock_context, api_event):
    """Test error when alarm is not found."""
    table = MagicMock()
    table.get_item.return_value = {}  # No Item
    
    with patch('lambdas.api.acknowledge_alarm.table', table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 404
        
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'NOT_FOUND'


def test_acknowledge_alarm_already_acknowledged(mock_context, api_event):
    """Test error when alarm is already acknowledged."""
    table = MagicMock()
    
    # Alarm already acknowledged
    acknowledged_alarm = {
        'PK': 'ALARM#alarm-001',
        'SK': 'METADATA',
        'alarm_id': 'alarm-001',
        'variable_id': 'PT-001',
        'area': 'pre-treatment',
        'severity': 'critical',
        'status': 'acknowledged',  # Already acknowledged
        'message': 'Temperature exceeds critical threshold',
        'value': Decimal('75.0'),
        'threshold': Decimal('69.0'),
        'created_at': '2024-01-15T10:00:00Z',
        'acknowledged_at': '2024-01-15T10:05:00Z'
    }
    
    table.get_item.return_value = {'Item': acknowledged_alarm}
    
    with patch('lambdas.api.acknowledge_alarm.table', table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 400
        
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'INVALID_STATE'
        assert 'active' in body['error']['message']


def test_acknowledge_alarm_resolved(mock_context, api_event):
    """Test error when alarm is already resolved."""
    table = MagicMock()
    
    # Alarm already resolved
    resolved_alarm = {
        'PK': 'ALARM#alarm-001',
        'SK': 'METADATA',
        'alarm_id': 'alarm-001',
        'variable_id': 'PT-001',
        'area': 'pre-treatment',
        'severity': 'critical',
        'status': 'resolved',  # Already resolved
        'message': 'Temperature exceeds critical threshold',
        'value': Decimal('75.0'),
        'threshold': Decimal('69.0'),
        'created_at': '2024-01-15T10:00:00Z',
        'acknowledged_at': '2024-01-15T10:05:00Z',
        'resolved_at': '2024-01-15T10:30:00Z'
    }
    
    table.get_item.return_value = {'Item': resolved_alarm}
    
    with patch('lambdas.api.acknowledge_alarm.table', table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 400
        
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'INVALID_STATE'


def test_acknowledge_alarm_invalid_json_body(mock_dynamodb_table, mock_context, api_event):
    """Test that invalid JSON in body is ignored gracefully."""
    api_event['body'] = 'invalid-json'
    
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        # Should still succeed, just without acknowledged_by
        assert response['statusCode'] == 200


def test_acknowledge_alarm_includes_all_fields(mock_dynamodb_table, mock_context, api_event):
    """Test that all required fields are included in response."""
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        alarm = body['data']['alarm']
        
        required_fields = [
            'alarm_id', 'variable_id', 'area', 'severity', 'status',
            'message', 'value', 'threshold', 'created_at', 'acknowledged_at'
        ]
        
        for field in required_fields:
            assert field in alarm, f"Missing field: {field}"


def test_acknowledge_alarm_converts_decimal_to_float(mock_dynamodb_table, mock_context, api_event):
    """Test that Decimal values from DynamoDB are converted to float."""
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        alarm = body['data']['alarm']
        
        # Check that numeric values are floats, not Decimals
        assert isinstance(alarm['value'], float)
        assert isinstance(alarm['threshold'], float)


def test_acknowledge_alarm_dynamodb_error(mock_context, api_event):
    """Test handling of DynamoDB errors."""
    from botocore.exceptions import ClientError
    
    table = MagicMock()
    table.get_item.side_effect = ClientError(
        {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
        'GetItem'
    )
    
    with patch('lambdas.api.acknowledge_alarm.table', table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 503
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'SERVICE_UNAVAILABLE'


def test_acknowledge_alarm_unexpected_error(mock_context, api_event):
    """Test handling of unexpected errors."""
    table = MagicMock()
    table.get_item.side_effect = Exception("Unexpected error")
    
    with patch('lambdas.api.acknowledge_alarm.table', table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'INTERNAL_ERROR'


def test_acknowledge_alarm_cors_headers(mock_dynamodb_table, mock_context, api_event):
    """Test that CORS headers are included in response."""
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Headers' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']


def test_acknowledge_alarm_response_format(mock_dynamodb_table, mock_context, api_event):
    """Test that response follows the standard format."""
    with patch('lambdas.api.acknowledge_alarm.table', mock_dynamodb_table):
        from lambdas.api.acknowledge_alarm import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Check standard response structure
        assert 'success' in body
        assert 'data' in body
        assert 'timestamp' in body
        assert 'request_id' in body
        
        # Validate timestamp format (ISO 8601)
        timestamp = body['timestamp']
        assert timestamp.endswith('Z')
        datetime.fromisoformat(timestamp.replace('Z', '+00:00'))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
