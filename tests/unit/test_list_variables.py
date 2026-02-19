"""
Unit tests for GET /variables Lambda handler.

Tests the list_variables handler that retrieves all variables from DynamoDB
and organizes them by area.
"""

import json
import os
from datetime import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_dynamodb_table():
    """Mock DynamoDB table with sample variables."""
    table = MagicMock()
    
    # Sample variables data
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'VAR#PT-001',
                'SK': 'METADATA',
                'variable_id': 'PT-001',
                'name': 'Temperature Tank 1',
                'area': 'pre-treatment',
                'unit': '°C',
                'data_type': 'float',
                'min_range': Decimal('60.0'),
                'max_range': Decimal('70.0'),
                'alarm_low': Decimal('61.0'),
                'alarm_high': Decimal('69.0'),
                'description': 'Pre-Treatment - Temperature Tank 1',
                'source_file': 'KMX-PA-PT-F-001.csv',
                'active': True
            },
            {
                'PK': 'VAR#PT-002',
                'SK': 'METADATA',
                'variable_id': 'PT-002',
                'name': 'pH Level',
                'area': 'pre-treatment',
                'unit': 'pH',
                'data_type': 'float',
                'min_range': Decimal('5.0'),
                'max_range': Decimal('7.0'),
                'alarm_low': Decimal('5.2'),
                'alarm_high': Decimal('6.8'),
                'description': 'Pre-Treatment - pH Level',
                'source_file': 'KMX-PA-PT-F-001.csv',
                'active': True
            },
            {
                'PK': 'VAR#ED-001',
                'SK': 'METADATA',
                'variable_id': 'ED-001',
                'name': 'Voltage',
                'area': 'e-coat',
                'unit': 'V',
                'data_type': 'float',
                'min_range': Decimal('200.0'),
                'max_range': Decimal('300.0'),
                'alarm_low': Decimal('210.0'),
                'alarm_high': Decimal('290.0'),
                'description': 'E-Coat - Voltage',
                'source_file': 'KMX-PA-PE-F-001.csv',
                'active': True
            },
            {
                'PK': 'VAR#PC-001',
                'SK': 'METADATA',
                'variable_id': 'PC-001',
                'name': 'Line Speed',
                'area': 'production-control',
                'unit': 'm/min',
                'data_type': 'float',
                'min_range': Decimal('10.0'),
                'max_range': Decimal('30.0'),
                'alarm_low': Decimal('12.0'),
                'alarm_high': Decimal('28.0'),
                'description': 'Production Control - Line Speed',
                'source_file': 'config',
                'active': True
            }
        ]
    }
    
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
        'path': '/variables',
        'headers': {
            'x-api-key': 'test-key'
        }
    }


def test_list_variables_success(mock_dynamodb_table, mock_context, api_event):
    """Test successful retrieval of variables."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        assert 'variables' in body['data']
        assert 'summary' in body['data']
        
        # Check organized structure
        variables = body['data']['variables']
        assert 'pre-treatment' in variables
        assert 'e-coat' in variables
        assert 'production-control' in variables
        
        # Check counts
        assert len(variables['pre-treatment']) == 2
        assert len(variables['e-coat']) == 1
        assert len(variables['production-control']) == 1
        
        # Check summary
        summary = body['data']['summary']
        assert summary['total'] == 4
        assert summary['by_area']['pre-treatment'] == 2
        assert summary['by_area']['e-coat'] == 1
        assert summary['by_area']['production-control'] == 1
        assert summary['active'] == 4


def test_list_variables_sorted_by_id(mock_dynamodb_table, mock_context, api_event):
    """Test that variables are sorted by variable_id within each area."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        pt_vars = body['data']['variables']['pre-treatment']
        assert pt_vars[0]['variable_id'] == 'PT-001'
        assert pt_vars[1]['variable_id'] == 'PT-002'


def test_list_variables_includes_all_fields(mock_dynamodb_table, mock_context, api_event):
    """Test that all required fields are included in response."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Check first variable has all fields
        var = body['data']['variables']['pre-treatment'][0]
        
        required_fields = [
            'variable_id', 'name', 'area', 'unit', 'data_type',
            'min_range', 'max_range', 'alarm_low', 'alarm_high',
            'description', 'source_file', 'active'
        ]
        
        for field in required_fields:
            assert field in var, f"Missing field: {field}"


def test_list_variables_converts_decimal_to_float(mock_dynamodb_table, mock_context, api_event):
    """Test that Decimal values from DynamoDB are converted to float."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        var = body['data']['variables']['pre-treatment'][0]
        
        # Check that numeric values are floats, not Decimals
        assert isinstance(var['min_range'], float)
        assert isinstance(var['max_range'], float)
        assert isinstance(var['alarm_low'], float)
        assert isinstance(var['alarm_high'], float)


def test_list_variables_empty_table(mock_context, api_event):
    """Test handling of empty table."""
    empty_table = MagicMock()
    empty_table.scan.return_value = {'Items': []}
    
    with patch('lambdas.api.list_variables.table', empty_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        
        assert body['data']['summary']['total'] == 0
        assert len(body['data']['variables']['pre-treatment']) == 0


def test_list_variables_pagination(mock_context, api_event):
    """Test handling of paginated DynamoDB scan results."""
    table = MagicMock()
    
    # First page
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'VAR#PT-001',
                'SK': 'METADATA',
                'variable_id': 'PT-001',
                'name': 'Var 1',
                'area': 'pre-treatment',
                'unit': '°C',
                'min_range': Decimal('60.0'),
                'max_range': Decimal('70.0'),
                'alarm_low': Decimal('61.0'),
                'alarm_high': Decimal('69.0'),
                'active': True
            }
        ],
        'LastEvaluatedKey': {'PK': 'VAR#PT-001'}
    }
    
    # Second page (no more pages)
    table.scan.side_effect = [
        table.scan.return_value,
        {
            'Items': [
                {
                    'PK': 'VAR#PT-002',
                    'SK': 'METADATA',
                    'variable_id': 'PT-002',
                    'name': 'Var 2',
                    'area': 'pre-treatment',
                    'unit': 'pH',
                    'min_range': Decimal('5.0'),
                    'max_range': Decimal('7.0'),
                    'alarm_low': Decimal('5.2'),
                    'alarm_high': Decimal('6.8'),
                    'active': True
                }
            ]
        }
    ]
    
    with patch('lambdas.api.list_variables.table', table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Should have combined both pages
        assert body['data']['summary']['total'] == 2


def test_list_variables_dynamodb_error(mock_context, api_event):
    """Test handling of DynamoDB errors."""
    from botocore.exceptions import ClientError
    
    table = MagicMock()
    table.scan.side_effect = ClientError(
        {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
        'Scan'
    )
    
    with patch('lambdas.api.list_variables.table', table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 503
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'SERVICE_UNAVAILABLE'


def test_list_variables_unexpected_error(mock_context, api_event):
    """Test handling of unexpected errors."""
    table = MagicMock()
    table.scan.side_effect = Exception("Unexpected error")
    
    with patch('lambdas.api.list_variables.table', table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        
        assert body['success'] is False
        assert body['error']['code'] == 'INTERNAL_ERROR'


def test_list_variables_cors_headers(mock_dynamodb_table, mock_context, api_event):
    """Test that CORS headers are included in response."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'
        assert 'Access-Control-Allow-Headers' in response['headers']
        assert 'Access-Control-Allow-Methods' in response['headers']


def test_list_variables_response_format(mock_dynamodb_table, mock_context, api_event):
    """Test that response follows the standard format."""
    with patch('lambdas.api.list_variables.table', mock_dynamodb_table):
        from lambdas.api.list_variables import handler
        
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


def test_list_variables_filters_non_metadata_items(mock_context, api_event):
    """Test that only items with SK='METADATA' are included."""
    table = MagicMock()
    table.scan.return_value = {
        'Items': [
            {
                'PK': 'VAR#PT-001',
                'SK': 'METADATA',
                'variable_id': 'PT-001',
                'name': 'Var 1',
                'area': 'pre-treatment',
                'unit': '°C',
                'min_range': Decimal('60.0'),
                'max_range': Decimal('70.0'),
                'alarm_low': Decimal('61.0'),
                'alarm_high': Decimal('69.0'),
                'active': True
            },
            {
                'PK': 'VAR#PT-001',
                'SK': 'STATS#2024-01-15',
                'some_other_data': 'should be filtered out'
            }
        ]
    }
    
    with patch('lambdas.api.list_variables.table', table):
        from lambdas.api.list_variables import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Should only include the METADATA item
        assert body['data']['summary']['total'] == 1
