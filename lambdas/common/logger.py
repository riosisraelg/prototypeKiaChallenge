"""
KIA Paint Shop IoT Prototype - Structured Logging Utility

This module provides structured JSON logging for all Lambda functions.
Logs include standardized fields for better searchability and analysis in CloudWatch.

Usage:
    from common.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Processing message", extra={'variable_id': 'PT-001', 'value': 65.5})
    logger.error("Failed to process", exc_info=True, extra={'error_type': 'ValidationError'})

Requirements: 9.2
"""

import logging
import json
import sys
import traceback
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in structured JSON format.
    
    Each log entry includes:
    - timestamp: ISO 8601 timestamp with timezone
    - level: Log level (INFO, WARNING, ERROR, etc.)
    - message: Log message
    - logger: Logger name
    - context: Additional context fields from 'extra' parameter
    - error_type: Exception class name (if applicable)
    - stack_trace: Full stack trace (for errors)
    - aws_request_id: Lambda request ID (if available)
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON string
        
        Args:
            record: LogRecord to format
            
        Returns:
            JSON string with structured log data
        """
        # Build base log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
        }
        
        # Add context from extra fields
        context = {}
        
        # Standard fields to exclude from context
        exclude_fields = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName',
            'levelname', 'levelno', 'lineno', 'module', 'msecs',
            'pathname', 'process', 'processName', 'relativeCreated',
            'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
            'getMessage', 'message'
        }
        
        # Extract custom fields from record
        for key, value in record.__dict__.items():
            if key not in exclude_fields and not key.startswith('_'):
                context[key] = value
        
        if context:
            log_entry['context'] = context
        
        # Add error information if present
        if record.exc_info:
            log_entry['error_type'] = record.exc_info[0].__name__ if record.exc_info[0] else 'Unknown'
            log_entry['stack_trace'] = self.formatException(record.exc_info)
        
        # Add source location
        log_entry['source'] = {
            'file': record.filename,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add Lambda request ID if available (set by Lambda runtime)
        if hasattr(record, 'aws_request_id'):
            log_entry['aws_request_id'] = record.aws_request_id
        
        return json.dumps(log_entry, default=str)


class StructuredLogger(logging.Logger):
    """
    Custom logger class with convenience methods for structured logging
    """
    
    def __init__(self, name: str, level: int = logging.INFO):
        super().__init__(name, level)
        self._aws_request_id: Optional[str] = None
    
    def set_request_id(self, request_id: str) -> None:
        """
        Set AWS Lambda request ID for all subsequent log entries
        
        Args:
            request_id: Lambda request ID from context
        """
        self._aws_request_id = request_id
    
    def _log_with_request_id(
        self,
        level: int,
        msg: str,
        args: tuple = (),
        exc_info: Any = None,
        extra: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        """
        Internal method to add request ID to log entries
        """
        if extra is None:
            extra = {}
        
        if self._aws_request_id:
            extra['aws_request_id'] = self._aws_request_id
        
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, **kwargs)
    
    def info_with_context(self, msg: str, **context) -> None:
        """
        Log info message with context fields
        
        Args:
            msg: Log message
            **context: Additional context fields
        """
        self.info(msg, extra=context)
    
    def warning_with_context(self, msg: str, **context) -> None:
        """
        Log warning message with context fields
        
        Args:
            msg: Log message
            **context: Additional context fields
        """
        self.warning(msg, extra=context)
    
    def error_with_context(
        self,
        msg: str,
        exc_info: bool = False,
        **context
    ) -> None:
        """
        Log error message with context fields
        
        Args:
            msg: Log message
            exc_info: Include exception info
            **context: Additional context fields
        """
        self.error(msg, exc_info=exc_info, extra=context)
    
    def log_exception(
        self,
        msg: str,
        exception: Exception,
        **context
    ) -> None:
        """
        Log exception with full context
        
        Args:
            msg: Log message
            exception: Exception object
            **context: Additional context fields
        """
        context['error_type'] = type(exception).__name__
        context['error_message'] = str(exception)
        
        self.error(msg, exc_info=True, extra=context)


def get_logger(name: str, level: Optional[str] = None) -> StructuredLogger:
    """
    Get or create a structured logger
    
    Args:
        name: Logger name (typically __name__)
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
               If None, uses LOG_LEVEL environment variable or defaults to INFO
    
    Returns:
        Configured StructuredLogger instance
    """
    import os
    
    # Determine log level
    if level is None:
        level = os.environ.get('LOG_LEVEL', 'INFO')
    
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Create or get logger
    logging.setLoggerClass(StructuredLogger)
    logger = logging.getLogger(name)
    
    # Only configure if not already configured
    if not logger.handlers:
        logger.setLevel(log_level)
        
        # Create console handler with structured formatter
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)
        handler.setFormatter(StructuredFormatter())
        
        logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
    
    return logger


def log_lambda_event(logger: logging.Logger, event: Dict[str, Any], context: Any) -> None:
    """
    Log Lambda invocation event with context
    
    Args:
        logger: Logger instance
        event: Lambda event
        context: Lambda context
    """
    logger.info(
        "Lambda invocation started",
        extra={
            'aws_request_id': context.request_id,
            'function_name': context.function_name,
            'function_version': context.function_version,
            'memory_limit_mb': context.memory_limit_in_mb,
            'remaining_time_ms': context.get_remaining_time_in_millis(),
            'event_keys': list(event.keys()) if isinstance(event, dict) else None
        }
    )


def log_lambda_result(
    logger: logging.Logger,
    context: Any,
    success: bool,
    duration_ms: float,
    **extra_context
) -> None:
    """
    Log Lambda invocation result
    
    Args:
        logger: Logger instance
        context: Lambda context
        success: Whether invocation was successful
        duration_ms: Execution duration in milliseconds
        **extra_context: Additional context fields
    """
    log_data = {
        'aws_request_id': context.request_id,
        'success': success,
        'duration_ms': duration_ms,
        'remaining_time_ms': context.get_remaining_time_in_millis(),
        **extra_context
    }
    
    if success:
        logger.info("Lambda invocation completed successfully", extra=log_data)
    else:
        logger.error("Lambda invocation failed", extra=log_data)


def log_error_with_context(
    logger: logging.Logger,
    error: Exception,
    operation: str,
    **context
) -> None:
    """
    Log error with full context and stack trace
    
    Args:
        logger: Logger instance
        error: Exception object
        operation: Operation that failed
        **context: Additional context fields
    """
    error_context = {
        'operation': operation,
        'error_type': type(error).__name__,
        'error_message': str(error),
        **context
    }
    
    logger.error(
        f"Error in {operation}: {str(error)}",
        exc_info=True,
        extra=error_context
    )


# Example usage and testing
if __name__ == '__main__':
    # Test structured logging
    logger = get_logger(__name__, level='DEBUG')
    
    logger.info("Simple info message")
    logger.info("Info with context", extra={'user_id': '123', 'action': 'login'})
    logger.warning("Warning message", extra={'threshold': 80, 'current': 85})
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        logger.error("Error occurred", exc_info=True, extra={'operation': 'test'})
    
    # Test convenience methods
    logger.info_with_context("Processing started", variable_id='PT-001', value=65.5)
    logger.error_with_context("Processing failed", exc_info=False, variable_id='PT-001')
