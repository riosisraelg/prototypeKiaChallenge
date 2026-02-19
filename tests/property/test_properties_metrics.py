"""
Property-based tests for CloudWatch custom metrics functionality.

Feature: kia-paint-shop-iot-prototype
Property 17: Envío de métricas a CloudWatch

These tests validate that custom metrics are correctly sent to CloudWatch
with appropriate dimensions and values.

Requirements: 9.1
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, patch, call
from datetime import datetime
import sys
import os

# Add lambdas directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambdas'))

from common.metrics import MetricsClient


# Hypothesis strategies
metric_names = st.sampled_from([
    'MessagesProcessed',
    'AlarmsGenerated',
    'OperationSuccess',
    'OperationError',
    'OperationLatency'
])

metric_values = st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)

metric_units = st.sampled_from([
    'Count',
    'Milliseconds',
    'Seconds',
    'Bytes',
    'Kilobytes',
    'Megabytes',
    'Percent'
])

function_names = st.sampled_from(['ingest', 'process', 'statistics', 'api'])

dimension_keys = st.sampled_from(['Operation', 'Status', 'ErrorType', 'Area', 'Severity'])
dimension_values = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))


class TestMetricsProperties:
    """Property-based tests for metrics functionality"""
    
    @given(
        function_name=function_names,
        metric_name=metric_names,
        value=metric_values,
        unit=metric_units
    )
    @settings(max_examples=100, deadline=None)
    def test_property_17_metrics_sent_to_cloudwatch(
        self,
        function_name,
        metric_name,
        value,
        unit
    ):
        """
        **Property 17: Envío de métricas a CloudWatch**
        
        **Validates: Requirements 9.1**
        
        For any operation in Lambda functions, custom metrics must be sent to
        CloudWatch with:
        - Correct namespace (KIA/PaintShop)
        - Appropriate dimensions (at minimum FunctionName)
        - Valid metric name, value, and unit
        - Timestamp
        
        This property ensures that all metrics are properly formatted and sent.
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            metrics = MetricsClient(function_name)
            
            # Act
            metrics.put_metric(metric_name, value, unit)
            metrics.flush()
            
            # Assert
            # Verify put_metric_data was called
            assert mock_cloudwatch.put_metric_data.called, \
                "CloudWatch put_metric_data should be called"
            
            # Get the call arguments
            call_args = mock_cloudwatch.put_metric_data.call_args
            
            # Verify namespace
            assert call_args[1]['Namespace'] == 'KIA/PaintShop', \
                "Metrics must use KIA/PaintShop namespace"
            
            # Verify metric data structure
            metric_data = call_args[1]['MetricData']
            assert len(metric_data) > 0, "At least one metric should be sent"
            
            metric = metric_data[0]
            
            # Verify metric name
            assert metric['MetricName'] == metric_name, \
                f"Metric name should be {metric_name}"
            
            # Verify metric value
            assert metric['Value'] == value, \
                f"Metric value should be {value}"
            
            # Verify metric unit
            assert metric['Unit'] == unit, \
                f"Metric unit should be {unit}"
            
            # Verify timestamp exists
            assert 'Timestamp' in metric, \
                "Metric must have a timestamp"
            
            # Verify dimensions include FunctionName
            dimensions = metric['Dimensions']
            function_dimension = next(
                (d for d in dimensions if d['Name'] == 'FunctionName'),
                None
            )
            assert function_dimension is not None, \
                "Metrics must include FunctionName dimension"
            assert function_dimension['Value'] == function_name, \
                f"FunctionName dimension should be {function_name}"
    
    @given(
        function_name=function_names,
        operation=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    )
    @settings(max_examples=50, deadline=None)
    def test_property_17_success_metrics_have_correct_dimensions(
        self,
        function_name,
        operation
    ):
        """
        **Property 17: Success metrics include Operation and Status dimensions**
        
        For any successful operation, the success metric must include:
        - FunctionName dimension
        - Operation dimension
        - Status dimension with value 'Success'
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            metrics = MetricsClient(function_name)
            
            # Act
            metrics.put_success_metric(operation)
            metrics.flush()
            
            # Assert
            call_args = mock_cloudwatch.put_metric_data.call_args
            metric_data = call_args[1]['MetricData']
            metric = metric_data[0]
            
            # Verify metric name
            assert metric['MetricName'] == 'OperationSuccess', \
                "Success metrics should use OperationSuccess metric name"
            
            # Verify dimensions
            dimensions = {d['Name']: d['Value'] for d in metric['Dimensions']}
            
            assert 'FunctionName' in dimensions, \
                "Success metrics must include FunctionName dimension"
            assert dimensions['FunctionName'] == function_name
            
            assert 'Operation' in dimensions, \
                "Success metrics must include Operation dimension"
            assert dimensions['Operation'] == operation
            
            assert 'Status' in dimensions, \
                "Success metrics must include Status dimension"
            assert dimensions['Status'] == 'Success'
    
    @given(
        function_name=function_names,
        operation=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        error_type=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))
    )
    @settings(max_examples=50, deadline=None)
    def test_property_17_error_metrics_have_correct_dimensions(
        self,
        function_name,
        operation,
        error_type
    ):
        """
        **Property 17: Error metrics include Operation, Status, and ErrorType dimensions**
        
        For any failed operation, the error metric must include:
        - FunctionName dimension
        - Operation dimension
        - Status dimension with value 'Error'
        - ErrorType dimension
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            metrics = MetricsClient(function_name)
            
            # Act
            metrics.put_error_metric(operation, error_type)
            metrics.flush()
            
            # Assert
            call_args = mock_cloudwatch.put_metric_data.call_args
            metric_data = call_args[1]['MetricData']
            metric = metric_data[0]
            
            # Verify metric name
            assert metric['MetricName'] == 'OperationError', \
                "Error metrics should use OperationError metric name"
            
            # Verify dimensions
            dimensions = {d['Name']: d['Value'] for d in metric['Dimensions']}
            
            assert 'FunctionName' in dimensions
            assert dimensions['FunctionName'] == function_name
            
            assert 'Operation' in dimensions
            assert dimensions['Operation'] == operation
            
            assert 'Status' in dimensions
            assert dimensions['Status'] == 'Error'
            
            assert 'ErrorType' in dimensions
            assert dimensions['ErrorType'] == error_type
    
    @given(
        function_name=function_names,
        operation=st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        latency=st.floats(min_value=0, max_value=60000, allow_nan=False, allow_infinity=False)
    )
    @settings(max_examples=50, deadline=None)
    def test_property_17_latency_metrics_use_milliseconds(
        self,
        function_name,
        operation,
        latency
    ):
        """
        **Property 17: Latency metrics use Milliseconds unit**
        
        For any operation latency metric, the unit must be Milliseconds.
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            metrics = MetricsClient(function_name)
            
            # Act
            metrics.put_latency_metric(operation, latency)
            metrics.flush()
            
            # Assert
            call_args = mock_cloudwatch.put_metric_data.call_args
            metric_data = call_args[1]['MetricData']
            metric = metric_data[0]
            
            # Verify metric name
            assert metric['MetricName'] == 'OperationLatency'
            
            # Verify unit is Milliseconds
            assert metric['Unit'] == 'Milliseconds', \
                "Latency metrics must use Milliseconds unit"
            
            # Verify value
            assert metric['Value'] == latency
    
    @given(
        function_name=function_names,
        num_metrics=st.integers(min_value=1, max_value=25)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_17_metrics_batched_correctly(
        self,
        function_name,
        num_metrics
    ):
        """
        **Property 17: Metrics are batched in groups of max 20**
        
        CloudWatch allows maximum 20 metrics per put_metric_data call.
        The MetricsClient should batch metrics appropriately.
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            metrics = MetricsClient(function_name)
            
            # Act - add multiple metrics
            for i in range(num_metrics):
                metrics.put_metric(f'TestMetric{i}', float(i), 'Count')
            
            metrics.flush()
            
            # Assert
            if num_metrics <= 20:
                # Should be one call
                assert mock_cloudwatch.put_metric_data.call_count == 1
                call_args = mock_cloudwatch.put_metric_data.call_args
                metric_data = call_args[1]['MetricData']
                assert len(metric_data) == num_metrics
            else:
                # Should be multiple calls
                expected_calls = (num_metrics + 19) // 20  # Ceiling division
                assert mock_cloudwatch.put_metric_data.call_count == expected_calls
                
                # Verify total metrics sent
                total_metrics = 0
                for call in mock_cloudwatch.put_metric_data.call_args_list:
                    metric_data = call[1]['MetricData']
                    assert len(metric_data) <= 20, \
                        "Each batch should have at most 20 metrics"
                    total_metrics += len(metric_data)
                
                assert total_metrics == num_metrics, \
                    f"Total metrics sent ({total_metrics}) should equal metrics added ({num_metrics})"
    
    @given(
        function_name=function_names,
        metric_name=metric_names,
        value=metric_values
    )
    @settings(max_examples=50, deadline=None)
    def test_property_17_context_manager_flushes_metrics(
        self,
        function_name,
        metric_name,
        value
    ):
        """
        **Property 17: Context manager automatically flushes metrics**
        
        When using MetricsClient as a context manager, metrics should be
        automatically flushed on exit.
        """
        # Arrange
        with patch('boto3.client') as mock_boto_client:
            mock_cloudwatch = Mock()
            mock_boto_client.return_value = mock_cloudwatch
            
            # Act
            with MetricsClient(function_name) as metrics:
                metrics.put_metric(metric_name, value)
                # Don't call flush explicitly
            
            # Assert - metrics should be flushed on context exit
            assert mock_cloudwatch.put_metric_data.called, \
                "Metrics should be automatically flushed when exiting context manager"
            
            call_args = mock_cloudwatch.put_metric_data.call_args
            metric_data = call_args[1]['MetricData']
            assert len(metric_data) > 0, \
                "At least one metric should be sent"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
