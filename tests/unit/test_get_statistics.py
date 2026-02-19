"""
Unit tests for GET /statistics/{variable_id} Lambda handler.

Tests the get_statistics handler that retrieves aggregated statistics
for a variable over the last 24 hours.
"""

import json
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_statistics_table():
    """Mock DynamoDB statistics table."""
    table = MagicMock()
    
    # Sample statistics data
    now = datetime.now(timezone.utc)
    
    sample_stats = [
        {
            'PK': 'PT-001',
            'SK': f"STATS#{(now - timedelta(hours=2)).isoformat().replace('+00:00', 'Z')}",
            'variable_id': 'PT-001',
            'window_start': (now - timedelta(hours=2)).isoformat().replace('+00:00', 'Z'),
            'window_end': (now - timedelta(hours=2, minutes=-10)).isoformat().replace('+00:00', 'Z'),
            'window_minutes': 10,
            'count': 20,
            'avg': Decimal('65.5'),
            'min': Decimal('64.0'),
            'max': Decimal('67.0'),
            'stddev': Decimal('0.8')
        },
        {
            'PK': 'PT-001',
            'SK': f"STATS#{(now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z')}",
            'variable_id': 'PT-001',
            'window_start': (now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
            'window_end': (now - timedelta(hours=1, minutes=-10)).isoformat().replace('+00:00', 'Z'),
            'window_minutes': 10,
            'count': 20,
            'avg': Decimal('66.0'),
            'min': Decimal('65.0'),
            'max': Decimal('68.0'),
            'stddev': Decimal('0.9')
        }
    ]
    
    table.query.return_value = {'Items': sample_stats}
    
    return table


@pytest.fixture
def mock_variables_metadata_table():
    """Mock DynamoDB variables metadata table."""
    table = MagicMock()
    
    table.get_item.return_value = {
        'Item': {
            'PK': 'VAR#PT-001',
            'SK': 'METADATA',
            'variable_id': 'PT-001',
            'name': 'Temperature Tank 1',
            'unit': '°C',
            'area': 'pre-treatment'
        }
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
        'path': '/statistics/PT-001',
        'pathParameters': {
            'variable_id': 'PT-001'
        },
        'headers': {
            'x-api-key': 'test-key'
        }
    }


def test_get_statistics_success(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test successful retrieval of statistics."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        
        body = json.loads(response['body'])
        assert body['success'] is True
        assert 'data' in body
        
        data = body['data']
        assert data['variable_id'] == 'PT-001'
        assert data['variable_name'] == 'Temperature Tank 1'
        assert data['unit'] == '°C'
        assert 'time_range' in data
        assert 'overall' in data
        assert 'windows' in data


def test_get_statistics_includes_time_range(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that time range is included in response."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        time_range = body['data']['time_range']
        assert 'start' in time_range
        assert 'end' in time_range
        assert time_range['hours'] == 24


def test_get_statistics_includes_overall_stats(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that overall statistics are calculated correctly."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        overall = body['data']['overall']
        assert 'avg' in overall
        assert 'min' in overall
        assert 'max' in overall
        assert 'total_samples' in overall
        assert 'windows_count' in overall
        
        # Check values
        assert overall['windows_count'] == 2
        assert overall['total_samples'] == 40  # 20 + 20
        assert overall['min'] == 64.0
        assert overall['max'] == 68.0


def test_get_statistics_includes_windows(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that individual statistics windows are included."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        windows = body['data']['windows']
        assert len(windows) == 2
        
        # Check first window
        window = windows[0]
        assert 'window_start' in window
        assert 'window_end' in window
        assert 'window_minutes' in window
        assert 'count' in window
        assert 'avg' in window
        assert 'min' in window
        assert 'max' in window
        assert 'stddev' in window


def test_get_statistics_converts_decimal_to_float(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that Decimal values from DynamoDB are converted to float."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        window = body['data']['windows'][0]
        
        # Check that numeric values are floats, not Decimals
        assert isinstance(window['avg'], float)
        assert isinstance(window['min'], float)
        assert isinstance(window['max'], float)
        assert isinstance(window['stddev'], float)


def test_get_statistics_missing_variable_id(mock_statistics_table, mock_variables_metadata_table, mock_context):
    """Test error when variable_id is missing."""
    event = {
        'httpMethod': 'GET',
        'path': '/statistics',
        'pathParameters': None,
        'headers': {'x-api-key': 'test-key'}
    }
    
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(event, mock_context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'VALIDATION_ERROR'


def test_get_statistics_variable_not_found(mock_statistics_table, mock_context, api_event):
    """Test error when variable is not found."""
    metadata_table = MagicMock()
    metadata_table.get_item.return_value = {}  # No Item
    
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'NOT_FOUND'


def test_get_statistics_no_data(mock_variables_metadata_table, mock_context, api_event):
    """Test handling when no statistics data is available."""
    stats_table = MagicMock()
    stats_table.query.return_value = {'Items': []}
    
    with patch('lambdas.api.get_statistics.statistics_table', stats_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        
        assert body['data']['overall'] is None
        assert len(body['data']['windows']) == 0


def test_get_statistics_pagination(mock_variables_metadata_table, mock_context, api_event):
    """Test handling of paginated DynamoDB query results."""
    stats_table = MagicMock()
    
    now = datetime.now(timezone.utc)
    
    # First page
    stats_table.query.return_value = {
        'Items': [
            {
                'PK': 'PT-001',
                'SK': f"STATS#{(now - timedelta(hours=2)).isoformat().replace('+00:00', 'Z')}",
                'variable_id': 'PT-001',
                'window_start': (now - timedelta(hours=2)).isoformat().replace('+00:00', 'Z'),
                'window_end': (now - timedelta(hours=2, minutes=-10)).isoformat().replace('+00:00', 'Z'),
                'window_minutes': 10,
                'count': 20,
                'avg': Decimal('65.5'),
                'min': Decimal('64.0'),
                'max': Decimal('67.0'),
                'stddev': Decimal('0.8')
            }
        ],
        'LastEvaluatedKey': {'PK': 'PT-001'}
    }
    
    # Second page
    stats_table.query.side_effect = [
        stats_table.query.return_value,
        {
            'Items': [
                {
                    'PK': 'PT-001',
                    'SK': f"STATS#{(now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z')}",
                    'variable_id': 'PT-001',
                    'window_start': (now - timedelta(hours=1)).isoformat().replace('+00:00', 'Z'),
                    'window_end': (now - timedelta(hours=1, minutes=-10)).isoformat().replace('+00:00', 'Z'),
                    'window_minutes': 10,
                    'count': 20,
                    'avg': Decimal('66.0'),
                    'min': Decimal('65.0'),
                    'max': Decimal('68.0'),
                    'stddev': Decimal('0.9')
                }
            ]
        }
    ]
    
    with patch('lambdas.api.get_statistics.statistics_table', stats_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        body = json.loads(response['body'])
        
        # Should have combined both pages
        assert len(body['data']['windows']) == 2


def test_get_statistics_dynamodb_error(mock_variables_metadata_table, mock_context, api_event):
    """Test handling of DynamoDB errors."""
    from botocore.exceptions import ClientError
    
    stats_table = MagicMock()
    stats_table.query.side_effect = ClientError(
        {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
        'Query'
    )
    
    with patch('lambdas.api.get_statistics.statistics_table', stats_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 503
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'SERVICE_UNAVAILABLE'


def test_get_statistics_unexpected_error(mock_variables_metadata_table, mock_context, api_event):
    """Test handling of unexpected errors."""
    stats_table = MagicMock()
    stats_table.query.side_effect = Exception("Unexpected error")
    
    with patch('lambdas.api.get_statistics.statistics_table', stats_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['success'] is False
        assert body['error']['code'] == 'INTERNAL_ERROR'


def test_get_statistics_cors_headers(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that CORS headers are included in response."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
        response = handler(api_event, mock_context)
        
        assert 'Access-Control-Allow-Origin' in response['headers']
        assert response['headers']['Access-Control-Allow-Origin'] == '*'


def test_get_statistics_response_format(mock_statistics_table, mock_variables_metadata_table, mock_context, api_event):
    """Test that response follows the standard format."""
    with patch('lambdas.api.get_statistics.statistics_table', mock_statistics_table), \
         patch('lambdas.api.get_statistics.variables_metadata_table', mock_variables_metadata_table):
        from lambdas.api.get_statistics import handler
        
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
