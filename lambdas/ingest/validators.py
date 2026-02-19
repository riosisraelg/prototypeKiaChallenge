"""
Validation functions for IoT message payloads.

This module provides validation for incoming MQTT messages from IoT Core,
ensuring data integrity before processing and storage.
"""

import json
from typing import Dict, Any, Tuple
from datetime import datetime


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_json_format(payload: Any) -> Tuple[bool, str]:
    """
    Validate that payload is valid JSON format.
    
    Args:
        payload: The payload to validate (can be string, dict, or other)
        
    Returns:
        Tuple of (is_valid, error_message)
        - is_valid: True if valid JSON, False otherwise
        - error_message: Empty string if valid, error description if invalid
    """
    # If already a dict, it's valid JSON
    if isinstance(payload, dict):
        return True, ""
    
    # If string, try to parse as JSON
    if isinstance(payload, str):
        try:
            json.loads(payload)
            return True, ""
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON format: {str(e)}"
    
    # Any other type is invalid
    return False, f"Payload must be JSON string or dict, got {type(payload).__name__}"


def validate_message_schema(message: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that message contains all required fields with correct types.
    
    Required fields:
    - variable_id (str): Variable identifier
    - area (str): Area name (pre-treatment, e-coat, production-control)
    - timestamp (str): ISO 8601 timestamp
    - value (float/int): Measured value
    - unit (str): Unit of measurement
    
    Args:
        message: The message dict to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import math
    
    required_fields = {
        'variable_id': str,
        'area': str,
        'timestamp': str,
        'value': (int, float),
        'unit': str
    }
    
    # Check all required fields are present
    for field, expected_type in required_fields.items():
        if field not in message:
            return False, f"Missing required field: {field}"
        
        # Check type
        if not isinstance(message[field], expected_type):
            return False, f"Field '{field}' must be of type {expected_type}, got {type(message[field]).__name__}"
    
    # Validate value is not NaN or infinity
    if isinstance(message['value'], float):
        if math.isnan(message['value']):
            return False, "Value cannot be NaN"
        if math.isinf(message['value']):
            return False, "Value cannot be infinity"
    
    # Validate area is one of the allowed values
    valid_areas = ['pre-treatment', 'e-coat', 'production-control']
    if message['area'] not in valid_areas:
        return False, f"Invalid area '{message['area']}', must be one of: {', '.join(valid_areas)}"
    
    # Validate timestamp format (ISO 8601)
    try:
        datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        return False, f"Invalid timestamp format: {str(e)}"
    
    # Validate variable_id is not empty
    if not message['variable_id'].strip():
        return False, "variable_id cannot be empty"
    
    return True, ""


def validate_value_range(value: float, min_range: float = None, max_range: float = None) -> Tuple[bool, str]:
    """
    Validate that value is within physically possible range.
    
    Args:
        value: The value to validate
        min_range: Minimum allowed value (optional)
        max_range: Maximum allowed value (optional)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check for NaN or infinity
    if not isinstance(value, (int, float)):
        return False, f"Value must be numeric, got {type(value).__name__}"
    
    import math
    if math.isnan(value):
        return False, "Value cannot be NaN"
    
    if math.isinf(value):
        return False, "Value cannot be infinity"
    
    # Check range if provided
    if min_range is not None and value < min_range:
        return False, f"Value {value} below minimum range {min_range}"
    
    if max_range is not None and value > max_range:
        return False, f"Value {value} above maximum range {max_range}"
    
    return True, ""


def validate_message(payload: Any) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Complete validation of an IoT message payload.
    
    This function performs all validation steps:
    1. JSON format validation
    2. Schema validation (required fields and types)
    3. Value range validation (if metadata provided)
    
    Args:
        payload: The raw payload from IoT Core
        
    Returns:
        Tuple of (is_valid, error_message, parsed_message)
        - is_valid: True if all validations pass
        - error_message: Empty if valid, error description if invalid
        - parsed_message: Parsed dict if valid, empty dict if invalid
    """
    # Step 1: Validate JSON format
    is_valid, error = validate_json_format(payload)
    if not is_valid:
        return False, error, {}
    
    # Parse payload to dict
    if isinstance(payload, str):
        try:
            message = json.loads(payload)
        except json.JSONDecodeError as e:
            return False, f"Failed to parse JSON: {str(e)}", {}
    else:
        message = payload
    
    # Step 2: Validate schema
    is_valid, error = validate_message_schema(message)
    if not is_valid:
        return False, error, {}
    
    # Step 3: Validate value range (if metadata provided)
    if 'metadata' in message and isinstance(message['metadata'], dict):
        min_range = message['metadata'].get('min_range')
        max_range = message['metadata'].get('max_range')
        
        is_valid, error = validate_value_range(message['value'], min_range, max_range)
        if not is_valid:
            return False, error, {}
    
    return True, "", message
