"""
KIA Paint Shop IoT Prototype - CloudWatch Custom Metrics Utility

This module provides a centralized way to send custom metrics to CloudWatch
from all Lambda functions. Metrics are sent to the KIA/PaintShop namespace
with appropriate dimensions.

Usage:
    from common.metrics import MetricsClient
    
    metrics = MetricsClient(function_name='ingest')
    metrics.put_metric('MessagesProcessed', 1, unit='Count')
    metrics.put_metric('ProcessingLatency', 150, unit='Milliseconds')
"""

import boto3
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger()

class MetricsClient:
    """Client for sending custom metrics to CloudWatch"""
    
    NAMESPACE = 'KIA/PaintShop'
    
    def __init__(self, function_name: str):
        """
        Initialize metrics client
        
        Args:
            function_name: Name of the Lambda function (e.g., 'ingest', 'process')
        """
        self.cloudwatch = boto3.client('cloudwatch')
        self.function_name = function_name
        self.metrics_buffer = []
        
    def put_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = 'Count',
        dimensions: Optional[Dict[str, str]] = None
    ) -> None:
        """
        Send a custom metric to CloudWatch
        
        Args:
            metric_name: Name of the metric (e.g., 'MessagesProcessed')
            value: Metric value
            unit: CloudWatch unit (Count, Milliseconds, Bytes, etc.)
            dimensions: Additional dimensions beyond FunctionName
        """
        try:
            # Build dimensions
            metric_dimensions = [
                {'Name': 'FunctionName', 'Value': self.function_name}
            ]
            
            if dimensions:
                for key, val in dimensions.items():
                    metric_dimensions.append({'Name': key, 'Value': val})
            
            # Add to buffer
            metric_data = {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow(),
                'Dimensions': metric_dimensions
            }
            
            self.metrics_buffer.append(metric_data)
            
            # Flush if buffer is large
            if len(self.metrics_buffer) >= 20:
                self.flush()
                
        except Exception as e:
            logger.warning(f"Failed to buffer metric {metric_name}: {e}")
    
    def put_success_metric(self, operation: str) -> None:
        """
        Send a success metric for an operation
        
        Args:
            operation: Operation name (e.g., 'Ingest', 'ProcessAlarm')
        """
        self.put_metric(
            metric_name='OperationSuccess',
            value=1,
            unit='Count',
            dimensions={'Operation': operation, 'Status': 'Success'}
        )
    
    def put_error_metric(self, operation: str, error_type: str) -> None:
        """
        Send an error metric for an operation
        
        Args:
            operation: Operation name (e.g., 'Ingest', 'ProcessAlarm')
            error_type: Type of error (e.g., 'ValidationError', 'DynamoDBError')
        """
        self.put_metric(
            metric_name='OperationError',
            value=1,
            unit='Count',
            dimensions={
                'Operation': operation,
                'Status': 'Error',
                'ErrorType': error_type
            }
        )
    
    def put_latency_metric(self, operation: str, latency_ms: float) -> None:
        """
        Send a latency metric for an operation
        
        Args:
            operation: Operation name
            latency_ms: Latency in milliseconds
        """
        self.put_metric(
            metric_name='OperationLatency',
            value=latency_ms,
            unit='Milliseconds',
            dimensions={'Operation': operation}
        )
    
    def flush(self) -> None:
        """Flush all buffered metrics to CloudWatch"""
        if not self.metrics_buffer:
            return
        
        try:
            # CloudWatch allows max 20 metrics per request
            for i in range(0, len(self.metrics_buffer), 20):
                batch = self.metrics_buffer[i:i+20]
                
                self.cloudwatch.put_metric_data(
                    Namespace=self.NAMESPACE,
                    MetricData=batch
                )
            
            logger.info(f"Flushed {len(self.metrics_buffer)} metrics to CloudWatch")
            self.metrics_buffer = []
            
        except Exception as e:
            logger.error(f"Failed to flush metrics to CloudWatch: {e}")
            self.metrics_buffer = []
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - flush metrics"""
        self.flush()


def track_operation(function_name: str, operation: str):
    """
    Decorator to track operation metrics automatically
    
    Usage:
        @track_operation('ingest', 'ProcessMessage')
        def process_message(event):
            # Your code here
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            metrics = MetricsClient(function_name)
            start_time = datetime.utcnow()
            
            try:
                result = func(*args, **kwargs)
                
                # Calculate latency
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Send success metrics
                metrics.put_success_metric(operation)
                metrics.put_latency_metric(operation, latency_ms)
                metrics.flush()
                
                return result
                
            except Exception as e:
                # Calculate latency
                latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Send error metrics
                error_type = type(e).__name__
                metrics.put_error_metric(operation, error_type)
                metrics.put_latency_metric(operation, latency_ms)
                metrics.flush()
                
                raise
        
        return wrapper
    return decorator
