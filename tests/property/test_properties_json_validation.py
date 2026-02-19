"""
Property-based tests for JSON validation.

Feature: kia-paint-shop-iot-prototype
Property 6: Validación de formato JSON

Tests that the system validates JSON format correctly and rejects invalid payloads.

Validates: Requirements 2.3
"""

import sys
import json
from pathlib import Path

# Add lambdas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lambdas" / "ingest"))

from hypothesis import given, strategies as st, settings, assume
import pytest
from validators import (
    validate_json_format,
    validate_message_schema,
    validate_value_range,
    validate_message
)


# Feature: kia-paint-shop-iot-prototype, Property 6: Validación de formato JSON
@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_6_valid_json_is_accepted(variable_id, area, value, unit):
    """
    Property 6: Para cualquier mensaje con formato JSON válido y campos requeridos,
    el sistema debe aceptarlo y procesarlo correctamente.
    
    **Validates: Requirements 2.3**
    """
    # Create a valid message
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit
    }
    
    # Convert to JSON string
    json_payload = json.dumps(message)
    
    # Property: Valid JSON should be accepted
    is_valid, error, parsed = validate_message(json_payload)
    
    assert is_valid, f"Valid JSON was rejected: {error}"
    assert error == "", f"Valid JSON should have no error message, got: {error}"
    assert parsed == message, "Parsed message should match original"


@settings(max_examples=100)
@given(
    invalid_json=st.one_of(
        # Malformed JSON strings
        st.text(min_size=1).filter(lambda x: not x.strip().startswith('{')),
        st.just('{invalid json}'),
        st.just('{"key": undefined}'),
        st.just('{"key": }'),
        st.just('{key: "value"}'),  # Missing quotes on key
        st.just("{'key': 'value'}"),  # Single quotes instead of double
        st.just('{"key": "value",}'),  # Trailing comma
    )
)
def test_property_6_invalid_json_is_rejected(invalid_json):
    """
    Property 6: Para cualquier payload que no sea JSON válido,
    el sistema debe rechazarlo y registrar un error sin procesarlo.
    
    **Validates: Requirements 2.3**
    """
    # Assume the string is actually invalid JSON
    try:
        json.loads(invalid_json)
        assume(False)  # Skip if it's actually valid JSON
    except (json.JSONDecodeError, TypeError):
        pass  # Good, it's invalid
    
    # Property: Invalid JSON should be rejected
    is_valid, error, parsed = validate_message(invalid_json)
    
    assert not is_valid, f"Invalid JSON was accepted: {invalid_json}"
    assert error != "", "Invalid JSON should have an error message"
    assert parsed == {}, "Invalid JSON should return empty dict"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_6_dict_payload_is_accepted(variable_id, area, value, unit):
    """
    Property 6: Para cualquier payload que ya sea un dict válido,
    el sistema debe aceptarlo sin necesidad de parsing.
    
    **Validates: Requirements 2.3**
    """
    # Create a valid message as dict (already parsed)
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit
    }
    
    # Property: Valid dict should be accepted
    is_valid, error, parsed = validate_message(message)
    
    assert is_valid, f"Valid dict was rejected: {error}"
    assert error == "", f"Valid dict should have no error message, got: {error}"
    assert parsed == message, "Parsed message should match original"


@settings(max_examples=50)
@given(
    missing_field=st.sampled_from(['variable_id', 'area', 'timestamp', 'value', 'unit'])
)
def test_property_6_missing_required_fields_are_rejected(missing_field):
    """
    Property 6: Para cualquier mensaje JSON válido que falte un campo requerido,
    el sistema debe rechazarlo con un error descriptivo.
    
    **Validates: Requirements 2.3**
    """
    # Create a complete message
    message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': 65.5,
        'unit': '°C'
    }
    
    # Remove one required field
    del message[missing_field]
    
    # Property: Message with missing field should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, f"Message missing '{missing_field}' was accepted"
    assert missing_field in error.lower() or 'missing' in error.lower(), \
        f"Error message should mention missing field: {error}"
    assert parsed == {}, "Invalid message should return empty dict"


@settings(max_examples=50)
@given(
    invalid_area=st.text(min_size=1).filter(
        lambda x: x not in ['pre-treatment', 'e-coat', 'production-control']
    )
)
def test_property_6_invalid_area_is_rejected(invalid_area):
    """
    Property 6: Para cualquier mensaje con un área inválida,
    el sistema debe rechazarlo.
    
    **Validates: Requirements 2.3**
    """
    message = {
        'variable_id': 'TEST-001',
        'area': invalid_area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': 65.5,
        'unit': '°C'
    }
    
    # Property: Message with invalid area should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, f"Message with invalid area '{invalid_area}' was accepted"
    assert 'area' in error.lower() or 'invalid' in error.lower(), \
        f"Error message should mention invalid area: {error}"


@settings(max_examples=50)
@given(
    invalid_timestamp=st.one_of(
        st.just('not-a-timestamp'),
        st.just('2024-13-45'),  # Invalid month/day
        st.just('2024/01/15'),  # Wrong format
        st.just('15-01-2024'),  # Wrong format
        st.integers(),  # Wrong type
    )
)
def test_property_6_invalid_timestamp_is_rejected(invalid_timestamp):
    """
    Property 6: Para cualquier mensaje con timestamp inválido,
    el sistema debe rechazarlo.
    
    **Validates: Requirements 2.3**
    """
    message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': invalid_timestamp,
        'value': 65.5,
        'unit': '°C'
    }
    
    # Property: Message with invalid timestamp should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, f"Message with invalid timestamp '{invalid_timestamp}' was accepted"
    assert 'timestamp' in error.lower() or 'invalid' in error.lower() or 'type' in error.lower(), \
        f"Error message should mention invalid timestamp: {error}"


@settings(max_examples=50)
@given(
    invalid_value=st.one_of(
        st.just(float('nan')),
        st.just(float('inf')),
        st.just(float('-inf')),
        st.text(),  # String instead of number
    )
)
def test_property_6_invalid_value_types_are_rejected(invalid_value):
    """
    Property 6: Para cualquier mensaje con valor inválido (NaN, infinity, string),
    el sistema debe rechazarlo.
    
    **Validates: Requirements 2.3**
    """
    message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': invalid_value,
        'unit': '°C'
    }
    
    # Property: Message with invalid value should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, f"Message with invalid value '{invalid_value}' was accepted"
    assert 'value' in error.lower() or 'type' in error.lower() or 'nan' in error.lower() or 'infinity' in error.lower(), \
        f"Error message should mention invalid value: {error}"


@settings(max_examples=50)
@given(
    value=st.floats(min_value=1000.0, max_value=2000.0, allow_nan=False, allow_infinity=False),
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=500.0, allow_nan=False, allow_infinity=False),
)
def test_property_6_values_outside_range_are_rejected(value, min_range, max_range):
    """
    Property 6: Para cualquier mensaje con valor fuera del rango físicamente posible,
    el sistema debe rechazarlo cuando se proporciona metadata de rangos.
    
    **Validates: Requirements 2.3**
    """
    # Ensure value is actually outside the range
    assume(value > max_range or value < min_range)
    
    message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': '°C',
        'metadata': {
            'min_range': min_range,
            'max_range': max_range
        }
    }
    
    # Property: Message with value outside range should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, f"Message with value {value} outside range [{min_range}, {max_range}] was accepted"
    assert 'range' in error.lower() or 'above' in error.lower() or 'below' in error.lower(), \
        f"Error message should mention range violation: {error}"


@settings(max_examples=50)
@given(
    value=st.floats(min_value=50.0, max_value=150.0, allow_nan=False, allow_infinity=False),
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=500.0, allow_nan=False, allow_infinity=False),
)
def test_property_6_values_within_range_are_accepted(value, min_range, max_range):
    """
    Property 6: Para cualquier mensaje con valor dentro del rango especificado,
    el sistema debe aceptarlo.
    
    **Validates: Requirements 2.3**
    """
    # Ensure value is within the range
    assume(min_range <= value <= max_range)
    
    message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': '°C',
        'metadata': {
            'min_range': min_range,
            'max_range': max_range
        }
    }
    
    # Property: Message with value within range should be accepted
    is_valid, error, parsed = validate_message(message)
    
    assert is_valid, f"Message with value {value} within range [{min_range}, {max_range}] was rejected: {error}"
    assert error == "", f"Valid message should have no error: {error}"


@settings(max_examples=50)
@given(
    non_json_type=st.one_of(
        st.integers(),
        st.floats(allow_nan=False, allow_infinity=False),
        st.lists(st.integers()),
        st.booleans(),
        st.none(),
    )
)
def test_property_6_non_json_types_are_rejected(non_json_type):
    """
    Property 6: Para cualquier payload que no sea string o dict,
    el sistema debe rechazarlo.
    
    **Validates: Requirements 2.3**
    """
    # Property: Non-JSON types should be rejected
    is_valid, error = validate_json_format(non_json_type)
    
    assert not is_valid, f"Non-JSON type {type(non_json_type).__name__} was accepted"
    assert error != "", "Non-JSON type should have an error message"
    assert 'type' in error.lower() or 'json' in error.lower(), \
        f"Error message should mention type issue: {error}"


@settings(max_examples=50)
@given(
    empty_variable_id=st.just('   ')  # Whitespace only
)
def test_property_6_empty_variable_id_is_rejected(empty_variable_id):
    """
    Property 6: Para cualquier mensaje con variable_id vacío o solo espacios,
    el sistema debe rechazarlo.
    
    **Validates: Requirements 2.3**
    """
    message = {
        'variable_id': empty_variable_id,
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': 65.5,
        'unit': '°C'
    }
    
    # Property: Message with empty variable_id should be rejected
    is_valid, error, parsed = validate_message(message)
    
    assert not is_valid, "Message with empty variable_id was accepted"
    assert 'variable_id' in error.lower() or 'empty' in error.lower(), \
        f"Error message should mention empty variable_id: {error}"


def test_property_6_json_format_validation_function():
    """
    Property 6: La función validate_json_format debe manejar correctamente
    strings JSON válidos, dicts, y tipos inválidos.
    
    **Validates: Requirements 2.3**
    """
    # Valid JSON string
    valid_json = '{"key": "value"}'
    is_valid, error = validate_json_format(valid_json)
    assert is_valid, f"Valid JSON string rejected: {error}"
    assert error == ""
    
    # Valid dict
    valid_dict = {"key": "value"}
    is_valid, error = validate_json_format(valid_dict)
    assert is_valid, f"Valid dict rejected: {error}"
    assert error == ""
    
    # Invalid JSON string
    invalid_json = '{invalid}'
    is_valid, error = validate_json_format(invalid_json)
    assert not is_valid, "Invalid JSON string accepted"
    assert error != ""
    
    # Invalid type
    invalid_type = 123
    is_valid, error = validate_json_format(invalid_type)
    assert not is_valid, "Invalid type accepted"
    assert error != ""


def test_property_6_schema_validation_function():
    """
    Property 6: La función validate_message_schema debe verificar
    todos los campos requeridos y sus tipos.
    
    **Validates: Requirements 2.3**
    """
    # Valid message
    valid_message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': 65.5,
        'unit': '°C'
    }
    is_valid, error = validate_message_schema(valid_message)
    assert is_valid, f"Valid message rejected: {error}"
    assert error == ""
    
    # Missing field
    incomplete_message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        # Missing timestamp
        'value': 65.5,
        'unit': '°C'
    }
    is_valid, error = validate_message_schema(incomplete_message)
    assert not is_valid, "Message with missing field accepted"
    assert 'timestamp' in error.lower()
    
    # Wrong type
    wrong_type_message = {
        'variable_id': 'TEST-001',
        'area': 'pre-treatment',
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': 'not-a-number',  # Should be numeric
        'unit': '°C'
    }
    is_valid, error = validate_message_schema(wrong_type_message)
    assert not is_valid, "Message with wrong type accepted"
    assert 'value' in error.lower() or 'type' in error.lower()


def test_property_6_value_range_validation_function():
    """
    Property 6: La función validate_value_range debe verificar
    que los valores estén dentro de rangos físicamente posibles.
    
    **Validates: Requirements 2.3**
    """
    # Value within range
    is_valid, error = validate_value_range(50.0, 0.0, 100.0)
    assert is_valid, f"Value within range rejected: {error}"
    assert error == ""
    
    # Value below range
    is_valid, error = validate_value_range(-10.0, 0.0, 100.0)
    assert not is_valid, "Value below range accepted"
    assert 'below' in error.lower() or 'minimum' in error.lower()
    
    # Value above range
    is_valid, error = validate_value_range(150.0, 0.0, 100.0)
    assert not is_valid, "Value above range accepted"
    assert 'above' in error.lower() or 'maximum' in error.lower()
    
    # NaN value
    is_valid, error = validate_value_range(float('nan'))
    assert not is_valid, "NaN value accepted"
    assert 'nan' in error.lower()
    
    # Infinity value
    is_valid, error = validate_value_range(float('inf'))
    assert not is_valid, "Infinity value accepted"
    assert 'infinity' in error.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
