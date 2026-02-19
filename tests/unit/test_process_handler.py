"""
Unit tests for Lambda process handler.

Tests the Lambda function that processes sensor data, detects anomalies,
and stores alarms in DynamoDB.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add lambdas/process to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lambdas" / "process"))

from handler import (
    handler,
    get_variable_metadata,
    create_alarm_record,
    store_alarm,
    ProcessError
)
from anomaly_detector import AlarmResult, AlarmSeverity


class TestGetVariableMetadata:
    """Test suite for get_variable_metadata function."""
    
    @patch('handler.variables_table')
    def test_get_metadata_success(self, mock_table):
        """Test successful metadata retrieval."""
        mock_table.get_item.return_value = {
            'Item': {
                'PK': 'VAR#PT-TEMP-001',
                'SK': 'METADATA',
                'variable_id': 'PT-TEMP-001',
                'alarm_low': 60.0,
                'alarm_high': 70.0,
                'min_range': 50.0,
                'max_range': 80.0,
                'name': 'Pre-Treatment Temperature',
                'unit': '°C'
            }
        }
        
        result = get_variable_metadata('PT-TEMP-001')
        
        assert result is not None
        assert result['variable_id'] == 'PT-TEMP-001'
        assert result['alarm_low'] == 60.0
        assert result['alarm_high'] == 70.0
        mock_table.get_item.assert_called_once_with(
            Key={'PK': 'VAR#PT-TEMP-001', 'SK': 'METADATA'}
        )
    
    @patch('handler.variables_table')
    def test_get_metadata_not_found(self, mock_table):
        """Test metadata retrieval when variable doesn't exist."""
        mock_table.get_item.return_value = {}
        
        result = get_variable_metadata('NONEXISTENT')
        
        assert result is None
    
    @patch('handler.variables_table')
    def test_get_metadata_error(self, mock_table):
        """Test metadata retrieval with DynamoDB error."""
        from botocore.exceptions import ClientError
        
        mock_table.get_item.side_effect = ClientError(
            {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Service unavailable'}},
            'GetItem'
        )
        
        result = get_variable_metadata('PT-TEMP-001')
        
        assert result is None


class TestCreateAlarmRecord:
    """Test suite for create_alarm_record function."""
    
    def test_create_alarm_record_with_all_fields(self):
        """Test alarm record creation with all fields."""
        alarm_result = AlarmResult(
            is_alarm=True,
            severity=AlarmSeverity.CRITICAL,
            threshold_type='high',
            threshold_value=70.0,
            exceedance_percent=25.5,
            message='Temperature above high threshold',
            value=72.5
        )
        
        alarm_item = create_alarm_record(
            variable_id='PT-TEMP-001',
            area='pre-treatment',
            alarm_result=alarm_result,
            timestamp='2024-01-15T10:30:00.000Z',
            variable_name='Pre-Treatment Temperature'
        )
        
        assert alarm_item['PK'].startswith('ALARM#')
        assert alarm_item['SK'] == 'METADATA'
        assert 'alarm_id' in alarm_item
        assert alarm_item['variable_id'] == 'PT-TEMP-001'
        assert alarm_item['area'] == 'pre-treatment'
        assert alarm_item['severity'] == 'critical'
        assert alarm_item['status'] == 'active'
        assert alarm_item['message'] == 'Temperature above high threshold'
        assert alarm_item['value'] == 72.5
        assert alarm_item['threshold'] == 70.0
        assert alarm_item['threshold_type'] == 'high'
        assert alarm_item['exceedance_percent'] == 25.5
        assert alarm_item['sensor_timestamp'] == '2024-01-15T10:30:00.000Z'
        assert alarm_item['variable_name'] == 'Pre-Treatment Temperature'
        assert 'created_at' in alarm_item
    
    def test_create_alarm_record_without_variable_name(self):
        """Test alarm record creation without optional variable name."""
        alarm_result = AlarmResult(
            is_alarm=True,
            severity=AlarmSeverity.WARNING,
            threshold_type='low',
            threshold_value=60.0,
            exceedance_percent=5.0,
            message='Temperature below low threshold',
            value=59.0
        )
        
        alarm_item = create_alarm_record(
            variable_id='PT-TEMP-001',
            area='pre-treatment',
            alarm_result=alarm_result,
            timestamp='2024-01-15T10:30:00.000Z'
        )
        
        assert 'variable_name' not in alarm_item
        assert alarm_item['severity'] == 'warning'
    
    def test_alarm_id_is_unique(self):
        """Test that each alarm gets a unique ID."""
        alarm_result = AlarmResult(
            is_alarm=True,
            severity=AlarmSeverity.WARNING,
            threshold_type='high',
            threshold_value=70.0,
            exceedance_percent=5.0,
            message='Test alarm',
            value=71.0
        )
        
        alarm1 = create_alarm_record(
            variable_id='VAR-001',
            area='test',
            alarm_result=alarm_result,
            timestamp='2024-01-15T10:30:00.000Z'
        )
        
        alarm2 = create_alarm_record(
            variable_id='VAR-001',
            area='test',
            alarm_result=alarm_result,
            timestamp='2024-01-15T10:30:00.000Z'
        )
        
        assert alarm1['alarm_id'] != alarm2['alarm_id']


class TestStoreAlarm:
    """Test suite for store_alarm function."""
    
    @patch('handler.alarms_table')
    def test_store_alarm_success(self, mock_table):
        """Test successful alarm storage."""
        alarm_item = {
            'PK': 'ALARM#test-id',
            'SK': 'METADATA',
            'alarm_id': 'test-id',
            'variable_id': 'PT-TEMP-001',
            'severity': 'critical'
        }
        
        mock_table.put_item.return_value = {}
        
        result = store_alarm(alarm_item)
        
        assert result is True
        mock_table.put_item.assert_called_once_with(Item=alarm_item)
    
    @patch('handler.alarms_table')
    @patch('handler.time.sleep')
    def test_store_alarm_with_throttling(self, mock_sleep, mock_table):
        """Test alarm storage with DynamoDB throttling and retry."""
        from botocore.exceptions import ClientError
        
        alarm_item = {
            'PK': 'ALARM#test-id',
            'alarm_id': 'test-id',
            'variable_id': 'PT-TEMP-001',
            'severity': 'critical'
        }
        
        # First call fails with throttling, second succeeds
        mock_table.put_item.side_effect = [
            ClientError(
                {'Error': {'Code': 'ProvisionedThroughputExceededException', 'Message': 'Throttled'}},
                'PutItem'
            ),
            None  # Success on second call
        ]
        
        result = store_alarm(alarm_item, max_retries=3)
        
        assert result is True
        assert mock_table.put_item.call_count == 2
        mock_sleep.assert_called_once()
    
    @patch('handler.alarms_table')
    def test_store_alarm_table_not_found(self, mock_table):
        """Test alarm storage when table doesn't exist."""
        from botocore.exceptions import ClientError
        
        alarm_item = {'PK': 'ALARM#test-id', 'alarm_id': 'test-id'}
        
        mock_table.put_item.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Table not found'}},
            'PutItem'
        )
        
        with pytest.raises(ProcessError, match='does not exist'):
            store_alarm(alarm_item)


class TestHandler:
    """Test suite for Lambda handler function."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.context = Mock()
        self.context.request_id = 'test-request-id'
    
    @patch('handler.send_cloudwatch_metric')
    @patch('handler.store_alarm')
    @patch('handler.detector')
    @patch('handler.get_variable_metadata')
    def test_handler_with_alarm_detected(
        self,
        mock_get_metadata,
        mock_detector,
        mock_store_alarm,
        mock_send_metric
    ):
        """Test handler when alarm is detected."""
        # Setup event
        event = {
            'detail': {
                'variable_id': 'PT-TEMP-001',
                'area': 'pre-treatment',
                'value': 72.0,
                'timestamp': '2024-01-15T10:30:00.000Z',
                'unit': '°C'
            }
        }
        
        # Mock metadata
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'alarm_low': 60.0,
            'alarm_high': 70.0,
            'min_range': 50.0,
            'max_range': 80.0,
            'name': 'Pre-Treatment Temperature'
        }
        
        # Mock detector result
        mock_alarm_result = AlarmResult(
            is_alarm=True,
            severity=AlarmSeverity.CRITICAL,
            threshold_type='high',
            threshold_value=70.0,
            exceedance_percent=20.0,
            message='Temperature above high threshold',
            value=72.0
        )
        mock_detector.detect.return_value = mock_alarm_result
        
        # Mock store_alarm
        mock_store_alarm.return_value = True
        
        # Execute handler
        response = handler(event, self.context)
        
        # Verify response
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['alarm_generated'] is True
        assert body['alarm']['severity'] == 'critical'
        assert body['alarm']['variable_id'] == 'PT-TEMP-001'
        
        # Verify detector was called
        mock_detector.detect.assert_called_once()
        
        # Verify alarm was stored
        mock_store_alarm.assert_called_once()
        
        # Verify metrics were sent
        assert mock_send_metric.call_count >= 3  # At least AlarmsGenerated, AlarmsBySeverity, AlarmsByArea
    
    @patch('handler.send_cloudwatch_metric')
    @patch('handler.detector')
    @patch('handler.get_variable_metadata')
    def test_handler_no_alarm(
        self,
        mock_get_metadata,
        mock_detector,
        mock_send_metric
    ):
        """Test handler when no alarm is detected."""
        event = {
            'detail': {
                'variable_id': 'PT-TEMP-001',
                'area': 'pre-treatment',
                'value': 65.0,
                'timestamp': '2024-01-15T10:30:00.000Z',
                'unit': '°C'
            }
        }
        
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'alarm_low': 60.0,
            'alarm_high': 70.0,
            'min_range': 50.0,
            'max_range': 80.0
        }
        
        mock_alarm_result = AlarmResult(
            is_alarm=False,
            severity=None,
            threshold_type=None,
            threshold_value=None,
            exceedance_percent=None,
            message=None,
            value=65.0
        )
        mock_detector.detect.return_value = mock_alarm_result
        
        response = handler(event, self.context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['alarm_generated'] is False
        assert body['reason'] == 'Value within thresholds'
    
    @patch('handler.send_cloudwatch_metric')
    @patch('handler.get_variable_metadata')
    def test_handler_no_metadata(self, mock_get_metadata, mock_send_metric):
        """Test handler when variable metadata is not found."""
        event = {
            'detail': {
                'variable_id': 'UNKNOWN-VAR',
                'area': 'test',
                'value': 65.0,
                'timestamp': '2024-01-15T10:30:00.000Z'
            }
        }
        
        mock_get_metadata.return_value = None
        
        response = handler(event, self.context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['alarm_generated'] is False
        assert body['reason'] == 'No metadata found'
    
    @patch('handler.send_cloudwatch_metric')
    @patch('handler.get_variable_metadata')
    def test_handler_no_thresholds(self, mock_get_metadata, mock_send_metric):
        """Test handler when variable has no alarm thresholds defined."""
        event = {
            'detail': {
                'variable_id': 'PT-TEMP-001',
                'area': 'pre-treatment',
                'value': 65.0,
                'timestamp': '2024-01-15T10:30:00.000Z'
            }
        }
        
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'min_range': 50.0,
            'max_range': 80.0
            # No alarm_low or alarm_high
        }
        
        response = handler(event, self.context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True
        assert body['alarm_generated'] is False
        assert body['reason'] == 'No thresholds defined'
    
    @patch('handler.send_cloudwatch_metric')
    def test_handler_missing_required_fields(self, mock_send_metric):
        """Test handler with missing required fields."""
        event = {
            'detail': {
                'variable_id': 'PT-TEMP-001',
                # Missing area, value, timestamp
            }
        }
        
        response = handler(event, self.context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert body['success'] is False
        assert 'Missing required fields' in body['error']
    
    @patch('handler.send_cloudwatch_metric')
    @patch('handler.store_alarm')
    @patch('handler.detector')
    @patch('handler.get_variable_metadata')
    def test_handler_direct_invocation(
        self,
        mock_get_metadata,
        mock_detector,
        mock_store_alarm,
        mock_send_metric
    ):
        """Test handler with direct invocation (no EventBridge wrapper)."""
        # Event without 'detail' wrapper
        event = {
            'variable_id': 'PT-TEMP-001',
            'area': 'pre-treatment',
            'value': 65.0,
            'timestamp': '2024-01-15T10:30:00.000Z',
            'unit': '°C'
        }
        
        mock_get_metadata.return_value = {
            'variable_id': 'PT-TEMP-001',
            'alarm_low': 60.0,
            'alarm_high': 70.0
        }
        
        mock_alarm_result = AlarmResult(
            is_alarm=False,
            severity=None,
            threshold_type=None,
            threshold_value=None,
            exceedance_percent=None,
            message=None,
            value=65.0
        )
        mock_detector.detect.return_value = mock_alarm_result
        
        response = handler(event, self.context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['success'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
