"""
Unit tests for Lambda ingest handler.

Tests the ingestion logic including validation, enrichment, storage,
and EventBridge publishing.
"""

import json
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Mock boto3 and botocore before importing handler
sys.modules['boto3'] = MagicMock()
sys.modules['botocore'] = MagicMock()
sys.modules['botocore.exceptions'] = MagicMock()

# Add lambdas/ingest to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambdas/ingest'))

from handler import (
    calculate_ttl,
    enrich_message,
    build_dynamodb_item,
    handler
)


class TestCalculateTTL:
    """Test TTL calculation."""
    
    def test_calculate_ttl_default_30_days(self):
        """Test that TTL is calculated for 30 days in the future."""
        ttl = calculate_ttl(30)
        
        # TTL should be approximately 30 days from now
        expected_ttl = int((datetime.utcnow() + timedelta(days=30)).timestamp())
        
        # Allow 1 second tolerance
        assert abs(ttl - expected_ttl) <= 1
    
    def test_calculate_ttl_custom_days(self):
        """Test TTL calculation with custom days."""
        ttl = calculate_ttl(7)
        
        expected_ttl = int((datetime.utcnow() + timedelta(days=7)).timestamp())
        
        assert abs(ttl - expected_ttl) <= 1


class TestEnrichMessage:
    """Test message enrichment."""
    
    def test_enrich_message_adds_metadata(self):
        """Test that enrichment adds required metadata fields."""
        message = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C'
        }
        
        context = Mock()
        context.request_id = 'test-request-123'
        
        enriched = enrich_message(message, context)
        
        # Check that original fields are preserved
        assert enriched['variable_id'] == 'PT-TEMP-001'
        assert enriched['area'] == 'pre-treatment'
        assert enriched['value'] == 65.5
        
        # Check that new fields are added
        assert enriched['request_id'] == 'test-request-123'
        assert 'processing_timestamp' in enriched
        assert 'ingestion_time_ms' in enriched
        
        # Verify timestamp format
        assert enriched['processing_timestamp'].endswith('Z')
    
    def test_enrich_message_preserves_metadata(self):
        """Test that existing metadata is preserved."""
        message = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C',
            'metadata': {
                'min_range': 60.0,
                'max_range': 70.0
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-123'
        
        enriched = enrich_message(message, context)
        
        assert 'metadata' in enriched
        assert enriched['metadata']['min_range'] == 60.0


class TestBuildDynamoDBItem:
    """Test DynamoDB item construction."""
    
    def test_build_item_with_valid_message(self):
        """Test building DynamoDB item from valid message."""
        message = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C',
            'quality': 'good',
            'request_id': 'test-123',
            'processing_timestamp': '2024-01-15T10:30:01.000Z'
        }
        
        item = build_dynamodb_item(message)
        
        # Check partition key format
        assert item['PK'] == 'pre-treatment#PT-TEMP-001'
        
        # Check sort key format
        assert item['SK'].startswith('DATA#')
        assert item['SK'].split('#')[1].isdigit()
        
        # Check all required fields
        assert item['variable_id'] == 'PT-TEMP-001'
        assert item['area'] == 'pre-treatment'
        assert item['timestamp'] == '2024-01-15T10:30:00.000Z'
        assert item['value'] == 65.5
        assert item['unit'] == '°C'
        assert item['quality'] == 'good'
        assert item['request_id'] == 'test-123'
        
        # Check TTL is set
        assert 'ttl' in item
        assert isinstance(item['ttl'], int)
    
    def test_build_item_with_metadata(self):
        """Test that metadata is included in item."""
        message = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C',
            'metadata': {
                'min_range': 60.0,
                'max_range': 70.0,
                'alarm_low': 62.0,
                'alarm_high': 68.0
            }
        }
        
        item = build_dynamodb_item(message)
        
        assert 'metadata' in item
        assert item['metadata']['min_range'] == 60.0
        assert item['metadata']['alarm_high'] == 68.0
    
    def test_build_item_default_quality(self):
        """Test that quality defaults to 'good' if not provided."""
        message = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C'
        }
        
        item = build_dynamodb_item(message)
        
        assert item['quality'] == 'good'


class TestHandler:
    """Test Lambda handler function."""
    
    @patch('handler.table')
    @patch('handler.eventbridge')
    @patch('handler.send_cloudwatch_metric')
    def test_handler_success(self, mock_metric, mock_eventbridge, mock_table):
        """Test successful message processing."""
        # Setup mocks
        mock_table.put_item.return_value = {}
        mock_eventbridge.put_events.return_value = {'FailedEntryCount': 0}
        
        # Create test event
        event = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C',
            'metadata': {
                'min_range': 60.0,
                'max_range': 70.0
            }
        }
        
        context = Mock()
        context.request_id = 'test-request-123'
        
        # Call handler
        response = handler(event, context)
        
        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['variable_id'] == 'PT-TEMP-001'
        assert body['data']['stored'] is True
        
        # Verify DynamoDB was called
        mock_table.put_item.assert_called_once()
        
        # Verify EventBridge was called
        mock_eventbridge.put_events.assert_called_once()
    
    @patch('handler.send_cloudwatch_metric')
    def test_handler_validation_error(self, mock_metric):
        """Test handler with invalid message."""
        # Create invalid event (missing required field)
        event = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            # Missing timestamp
            'value': 65.5,
            'unit': '°C'
        }
        
        context = Mock()
        context.request_id = 'test-request-123'
        
        # Call handler
        response = handler(event, context)
        
        # Verify error response
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'error' in body
        assert body['error']['code'] == 'VALIDATION_ERROR'
    
    @patch('handler.table')
    @patch('handler.eventbridge')
    @patch('handler.send_cloudwatch_metric')
    def test_handler_eventbridge_failure_continues(self, mock_metric, mock_eventbridge, mock_table):
        """Test that EventBridge failure doesn't prevent DynamoDB storage."""
        # Setup mocks - DynamoDB succeeds, EventBridge fails
        mock_table.put_item.return_value = {}
        mock_eventbridge.put_events.return_value = {
            'FailedEntryCount': 1,
            'Entries': [{'ErrorMessage': 'Test error'}]
        }
        
        event = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'timestamp': '2024-01-15T10:30:00.000Z',
            'value': 65.5,
            'unit': '°C'
        }
        
        context = Mock()
        context.request_id = 'test-request-123'
        
        # Call handler
        response = handler(event, context)
        
        # Should still succeed even if EventBridge fails
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['data']['stored'] is True
        assert body['data']['eventbridge_published'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
