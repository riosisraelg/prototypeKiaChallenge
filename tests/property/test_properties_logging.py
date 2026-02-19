"""
Property-based tests for structured logging functionality.

Feature: kia-paint-shop-iot-prototype
Property 18: Logging estructurado de errores

These tests validate that error logging includes all required fields
in structured JSON format for CloudWatch analysis.

Requirements: 9.2
"""

import pytest
from hypothesis import given, strategies as st, settings
import json
import logging
from io import StringIO
import sys
import os

# Add lambdas directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../lambdas'))

from common.logger import get_logger, StructuredFormatter, log_error_with_context


# Hypothesis strategies
log_messages = st.text(min_size=1, max_size=200, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs')))
logger_names = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')) + '._')
error_types = st.sampled_from(['ValueError', 'KeyError', 'TypeError', 'RuntimeError', 'IOError'])
operations = st.text(min_size=1, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll')))


class TestLoggingProperties:
    """Property-based tests for structured logging"""
    
    @given(
        logger_name=logger_names,
        message=log_messages
    )
    @settings(max_examples=100, deadline=None)
    def test_property_18_logs_have_required_fields(
        self,
        logger_name,
        message
    ):
        """
        **Property 18: Logging estructurado de errores**
        
        **Validates: Requirements 9.2**
        
        For any log entry, the structured log must include:
        - timestamp: ISO 8601 format with timezone
        - level: Log level (INFO, WARNING, ERROR, etc.)
        - message: The log message
        - logger: Logger name
        - source: File, function, and line information
        
        This ensures all logs are searchable and analyzable in CloudWatch.
        """
        # Arrange - capture log output
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Act
        logger.info(message)
        
        # Get log output
        log_output = stream.getvalue().strip()
        
        # Assert - parse as JSON
        try:
            log_entry = json.loads(log_output)
        except json.JSONDecodeError as e:
            pytest.fail(f"Log output is not valid JSON: {e}\nOutput: {log_output}")
        
        # Verify required fields
        assert 'timestamp' in log_entry, \
            "Log entry must include timestamp"
        
        assert 'level' in log_entry, \
            "Log entry must include level"
        assert log_entry['level'] == 'INFO'
        
        assert 'message' in log_entry, \
            "Log entry must include message"
        assert log_entry['message'] == message
        
        assert 'logger' in log_entry, \
            "Log entry must include logger name"
        
        assert 'source' in log_entry, \
            "Log entry must include source information"
        
        source = log_entry['source']
        assert 'file' in source, "Source must include file"
        assert 'function' in source, "Source must include function"
        assert 'line' in source, "Source must include line number"
        
        # Verify timestamp format (ISO 8601 with Z)
        assert log_entry['timestamp'].endswith('Z'), \
            "Timestamp must be in ISO 8601 format with Z timezone"
    
    @given(
        logger_name=logger_names,
        message=log_messages,
        error_type=error_types
    )
    @settings(max_examples=50, deadline=None)
    def test_property_18_error_logs_include_exception_info(
        self,
        logger_name,
        message,
        error_type
    ):
        """
        **Property 18: Error logs include error_type and stack_trace**
        
        For any error log with exception info, the log must include:
        - error_type: Exception class name
        - stack_trace: Full stack trace
        """
        # Arrange
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        # Create exception
        exception_classes = {
            'ValueError': ValueError,
            'KeyError': KeyError,
            'TypeError': TypeError,
            'RuntimeError': RuntimeError,
            'IOError': IOError
        }
        
        exc_class = exception_classes[error_type]
        
        # Act - log error with exception
        try:
            raise exc_class("Test error")
        except exc_class:
            logger.error(message, exc_info=True)
        
        # Get log output
        log_output = stream.getvalue().strip()
        log_entry = json.loads(log_output)
        
        # Assert
        assert 'error_type' in log_entry, \
            "Error logs must include error_type"
        assert log_entry['error_type'] == error_type, \
            f"error_type should be {error_type}"
        
        assert 'stack_trace' in log_entry, \
            "Error logs must include stack_trace"
        assert len(log_entry['stack_trace']) > 0, \
            "stack_trace should not be empty"
        assert 'Traceback' in log_entry['stack_trace'], \
            "stack_trace should contain traceback information"
    
    @given(
        logger_name=logger_names,
        message=log_messages,
        context_key=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Ll',))),
        context_value=st.one_of(
            st.text(min_size=1, max_size=50),
            st.integers(min_value=0, max_value=1000000),
            st.floats(min_value=0, max_value=1000000, allow_nan=False, allow_infinity=False)
        )
    )
    @settings(max_examples=50, deadline=None)
    def test_property_18_logs_include_context_fields(
        self,
        logger_name,
        message,
        context_key,
        context_value
    ):
        """
        **Property 18: Logs include context fields from extra parameter**
        
        For any log with extra context, the context fields must be included
        in the structured log output.
        """
        # Arrange
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Act
        logger.info(message, extra={context_key: context_value})
        
        # Get log output
        log_output = stream.getvalue().strip()
        log_entry = json.loads(log_output)
        
        # Assert
        assert 'context' in log_entry, \
            "Logs with extra fields must include context"
        
        context = log_entry['context']
        assert context_key in context, \
            f"Context must include {context_key}"
        
        # Convert for comparison (JSON may change types)
        actual_value = context[context_key]
        if isinstance(context_value, float):
            assert abs(actual_value - context_value) < 0.01, \
                f"Context value should be approximately {context_value}"
        else:
            assert actual_value == context_value, \
                f"Context value should be {context_value}"
    
    @given(
        logger_name=logger_names,
        message=log_messages,
        level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    )
    @settings(max_examples=50, deadline=None)
    def test_property_18_log_level_correctly_recorded(
        self,
        logger_name,
        message,
        level
    ):
        """
        **Property 18: Log level is correctly recorded**
        
        For any log at any level, the level field must match the logging level.
        """
        # Arrange
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)  # Allow all levels
        
        # Act
        log_method = getattr(logger, level.lower())
        log_method(message)
        
        # Get log output
        log_output = stream.getvalue().strip()
        log_entry = json.loads(log_output)
        
        # Assert
        assert log_entry['level'] == level, \
            f"Log level should be {level}"
    
    @given(
        operation=operations,
        error_message=log_messages,
        variable_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Nd')) + '-')
    )
    @settings(max_examples=50, deadline=None)
    def test_property_18_error_with_context_helper(
        self,
        operation,
        error_message,
        variable_id
    ):
        """
        **Property 18: log_error_with_context includes all required fields**
        
        The log_error_with_context helper function must include:
        - operation field
        - error_type field
        - error_message field
        - Any additional context fields
        - Full stack trace
        """
        # Arrange
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger('test_logger')
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.ERROR)
        
        # Create exception
        error = ValueError(error_message)
        
        # Act
        try:
            raise error
        except ValueError as e:
            log_error_with_context(
                logger,
                e,
                operation,
                variable_id=variable_id
            )
        
        # Get log output
        log_output = stream.getvalue().strip()
        log_entry = json.loads(log_output)
        
        # Assert
        assert 'context' in log_entry, \
            "Error logs must include context"
        
        context = log_entry['context']
        
        assert 'operation' in context, \
            "Context must include operation"
        assert context['operation'] == operation
        
        assert 'error_type' in context, \
            "Context must include error_type"
        assert context['error_type'] == 'ValueError'
        
        assert 'error_message' in context, \
            "Context must include error_message"
        assert context['error_message'] == error_message
        
        assert 'variable_id' in context, \
            "Context must include custom fields"
        assert context['variable_id'] == variable_id
        
        assert 'stack_trace' in log_entry, \
            "Error logs must include stack_trace"
    
    @given(
        logger_name=logger_names,
        num_logs=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=20, deadline=None)
    def test_property_18_all_logs_are_valid_json(
        self,
        logger_name,
        num_logs
    ):
        """
        **Property 18: All log entries are valid JSON**
        
        For any sequence of log entries, each entry must be valid JSON
        that can be parsed independently.
        """
        # Arrange
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        
        logger = logging.getLogger(logger_name)
        logger.handlers = []
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Act - log multiple entries
        for i in range(num_logs):
            logger.info(f"Log entry {i}", extra={'index': i})
        
        # Get log output
        log_output = stream.getvalue()
        log_lines = log_output.strip().split('\n')
        
        # Assert - each line should be valid JSON
        assert len(log_lines) == num_logs, \
            f"Should have {num_logs} log lines"
        
        for i, line in enumerate(log_lines):
            try:
                log_entry = json.loads(line)
                assert 'message' in log_entry
                assert 'timestamp' in log_entry
                assert 'level' in log_entry
            except json.JSONDecodeError as e:
                pytest.fail(f"Log line {i} is not valid JSON: {e}\nLine: {line}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--hypothesis-show-statistics'])
