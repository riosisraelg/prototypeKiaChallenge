"""
Unit tests for GET /alarms Lambda handler.

Tests the list_alarms handler that retrieves alarms from DynamoDB,
optionally filtered by status (active, acknowledged, resolved).
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table with sample alarms."""
    table = MagicMock()
    
    # Sample alarms data
    sample_alarms = [
        {
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
        },
        {
            'PK': 'ALARM#alarm-002',
            'SK': 'METADATA',
            'alarm_id': 'alarm-002',
            'variable_id': 'PT-002',
            'area': 'pre-treatment',
            'severity': 'warning',
            'status': 'acknowledged',
            'message': 'pH level slightly low',
            'value': Decimal('5.1'),
            'threshold': Decimal('5.2'),
            'created_at': '2024-01-15T09:30:00Z',
            'acknowledged_at': '2024-01-15T09:35:00Z',
            'acknowledged_by': 'operator-1'
        },
        {
            'PK': 'ALARM#alarm-003',
            'SK': 'METADATA',
            'alarm_id': 'alarm-003',
            'variable_id': 'ED-001',
            'area': 'e-coat',
            'severity': 'warning',
            'status': 'resolved',
            'message': 'Voltage fluctuation detected',
            'value': Decimal('295.0'),
            'threshold': Decimal('290.0'),
            'created_at': '2024-01-15T08:00:00Z',
            'acknowledged_at': '2024-01-15T08:05:00Z',
            'resolved_at': '2024-01-15T08:30:00Z',
            'acknowledged_by': 'operator-2'
        }
    ]
    
    # Default: return all alarms (scan)
    table.scan.return_value = {'Items': sample_alarms}
    
    # Query by status (GSI)
    def query_side_effect(*args, **kwargs):
        status_filter = kwargs.get('ExpressionAttributeValues', {}).get(':status')
        filtered = [a for a in sample_alarms if a['status'] == status_filter]
        return {'Items': filtered}
    
    table.query.side_effect = query_side_effect
    
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
        'httpMethod': 'GET',
        'path': '/alarms',
        'headers': {
            'x-api-key': 'test-key'
        },
        'queryStringParameters': None
    }


def test_list_alarms_all_success(mock_dynamodb_table, mock_context, api_event):
    """Test successful retrieval of all alarms without filter."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'alarms' in body['data']
        assert 'summary' in body['data']
        
        # Check all alarms returned
        alarms = body['data']['alarms']
        assert len(alarms) == 3
        
        # Check summary
        summary = body['data']['summary']
        assert summary['total'] == 3
        assert summary['by_status']['active'] == 1
        assert summary['by_status']['acknowledged'] == 1
        assert summary['by_status']['resolved'] == 1
        assert summary['by_severity']['warning'] == 2
        assert summary['by_severity']['critical'] == 1


def test_list_alarms_filter_by_active(mock_dynamodb_table, mock_context, api_event):
    """Test filtering alarms by status=active."""
    api_event['queryStringParameters'] = {'status': 'active'}
    
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        alarms = body['data']['alarms']
        
        # Should only return active alarms
        assert len(alarms) == 1
        assert alarms[0]['status'] == 'active'
        assert alarms[0]['alarm_id'] == 'alarm-001'


def test_list_alarms_filter_by_acknowledged(mock_dynamodb_table, mock_context, api_event):
    """Test filtering alarms by status=acknowledged."""
    api_event['queryStringParameters'] = {'status': 'acknowledged'}
    
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        alarms = body['data']['alarms']
        
        # Should only return acknowledged alarms
        assert len(alarms) == 1
        assert alarms[0]['status'] == 'acknowledged'
        assert alarms[0]['alarm_id'] == 'alarm-002'


def test_list_alarms_filter_by_resolved(mock_dynamodb_table, mock_context, api_event):
    """Test filtering alarms by status=resolved."""
    api_event['queryStringParameters'] = {'status': 'resolved'}
    
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        alarms = body['data']['alarms']
        
        # Should only return resolved alarms
        assert len(alarms) == 1
        assert alarms[0]['status'] == 'resolved'
        assert alarms[0]['alarm_id'] == 'alarm-003'


def test_list_alarms_invalid_status(mock_dynamodb_table, mock_context, api_event):
    """Test validation error for invalid status filter."""
    api_event['queryStringParameters'] = {'status': 'invalid-status'}
    
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 400
        
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'VALIDATION_ERROR'
        assert 'inválido' in body['error']['message']


def test_list_alarms_sorted_by_created_at(mock_dynamodb_table, mock_context, api_event):
    """Test that alarms are sorted by created_at descending (most recent first)."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        alarms = body['data']['alarms']
        
        # Should be sorted descending by created_at
        assert alarms[0]['created_at'] == '2024-01-15T10:00:00Z'  # Most recent
        assert alarms[1]['created_at'] == '2024-01-15T09:30:00Z'
        assert alarms[2]['created_at'] == '2024-01-15T08:00:00Z'  # Oldest


def test_list_alarms_includes_all_fields(mock_dynamodb_table, mock_context, api_event):
    """Test that all required fields are included in response."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Check first alarm has all fields
        alarm = body['data']['alarms'][0]
        
        required_fields = [
            'alarm_id', 'variable_id', 'area', 'severity', 'status',
            'message', 'value', 'threshold', 'created_at'
        ]
        
        for field in required_fields:
            assert field in alarm, f"Missing field: {field}"


def test_list_alarms_converts_decimal_to_float(mock_dynamodb_table, mock_context, api_event):
    """Test that Decimal values from DynamoDB are converted to float."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        alarm = body['data']['alarms'][0]
        
        # Check that numeric values are floats, not Decimals
        assert isinstance(alarm['value'], float)
        assert isinstance(alarm['threshold'], float)


def test_list_alarms_empty_table(mock_context, api_event):
    """Test handling of empty table."""
    empty_table = MagicMock()
    empty_table.scan.return_value = {'Items': []}
    
    with patch('lambdas.api.list_alarms.table', empty_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        
        assert body['data']['summary']['total'] == 0
        assert len(body['data']['alarms']) == 0


def test_list_alarms_pagination(mock_context, api_event):
    """Test handling of paginated DynamoDB scan results."""
    table = MagicMock()
    
    # First page
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'ALARM#alarm-001',
                'SK': 'METADATA',
                'alarm_id': 'alarm-001',
                'variable_id': 'PT-001',
                'area': 'pre-treatment',
                'severity': 'critical',
                'status': 'active',
                'message': 'Test alarm 1',
                'value': Decimal('75.0'),
                'threshold': Decimal('69.0'),
                'created_at': '2024-01-15T10:00:00Z'
            }
        ],
        'LastEvaluatedKey': {'PK': 'ALARM#alarm-001'}
    }
    
    # Second page (no more pages)
    table.scan.side_effect = [
        table.scan.return_value,
        {
            'Items': [
                {
                    'PK': 'ALARM#alarm-002',
                    'SK': 'METADATA',
                    'alarm_id': 'alarm-002',
                    'variable_id': 'PT-002',
                    'area': 'pre-treatment',
                    'severity': 'warning',
                    'status': 'active',
                    'message': 'Test alarm 2',
                    'value': Decimal('5.1'),
                    'threshold': Decimal('5.2'),
                    'created_at': '2024-01-15T09:30:00Z'
                }
            ]
        }
    ]
    
    with patch('lambdas.api.list_alarms.table', table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Should have combined both pages
        assert body['data']['summary']['total'] == 2


def test_list_alarms_dynamodb_error(mock_context, api_event):
    """Test handling of DynamoDB errors."""
    from botocore.exceptions import ClientError
    
    table = MagicMock()
    table.scan.side_effect = ClientError(
        {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
        'Scan'
    )
    
    with patch('lambdas.api.list_alarms.table', table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 503
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'SERVICE_UNAVAILABLE'


def test_list_alarms_unexpected_error(mock_context, api_event):
    """Test handling of unexpected errors."""
    table = MagicMock()
    table.scan.side_effect = Exception("Unexpected error")
    
    with patch('lambdas.api.list_alarms.table', table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'INTERNAL_ERROR'


def test_list_alarms_cors_headers(mock_dynamodb_table, mock_context, api_event):
    """Test that CORS headers are included in response."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Headers' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']


def test_list_alarms_response_format(mock_dynamodb_table, mock_context, api_event):
    """Test that response follows the standard format."""
    with patch('lambdas.api.list_alarms.table', mock_dynamodb_table):
        from lambdas.api.list_alarms import handler
        
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


def test_list_alarms_filters_non_metadata_items(mock_context, api_event):
    """Test that only items with SK='METADATA' are included."""
    table = MagicMock()
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'ALARM#alarm-001',
                'SK': 'METADATA',
                'alarm_id': 'alarm-001',
                'variable_id': 'PT-001',
                'area': 'pre-treatment',
                'severity': 'critical',
                'status': 'active',
                'message': 'Test alarm',
                'value': Decimal('75.0'),
                'threshold': Decimal('69.0'),
                'created_at': '2024-01-15T10:00:00Z'
            },
            {
                'PK': 'ALARM#alarm-001',
                'SK': 'HISTORY#2024-01-15',
                'some_other_data': 'should be filtered out'
            }
        ]
    }
    
    with patch('lambdas.api.list_alarms.table', table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Should only include the METADATA item
        assert body['data']['summary']['total'] == 1


def test_list_alarms_optional_fields(mock_context, api_event):
    """Test that optional fields (acknowledged_at, resolved_at, acknowledged_by) are handled correctly."""
    table = MagicMock()
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'ALARM#alarm-001',
                'SK': 'METADATA',
                'alarm_id': 'alarm-001',
                'variable_id': 'PT-001',
                'area': 'pre-treatment',
                'severity': 'critical',
                'status': 'active',
                'message': 'Test alarm',
                'value': Decimal('75.0'),
                'threshold': Decimal('69.0'),
                'created_at': '2024-01-15T10:00:00Z'
                # No acknowledged_at, resolved_at, acknowledged_by
            }
        ]
    }
    
    with patch('lambdas.api.list_alarms.table', table):
        from lambdas.api.list_alarms import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        alarm = body['data']['alarms'][0]
        
        # Optional fields should be present but None
        assert 'acknowledged_at' in alarm
        assert 'resolved_at' in alarm
        assert 'acknowledged_by' in alarm
        assert alarm['acknowledged_at'] is None
        assert alarm['resolved_at'] is None
        assert alarm['acknowledged_by'] is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
