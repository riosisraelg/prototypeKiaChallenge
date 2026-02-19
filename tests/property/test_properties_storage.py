"""
Property-based tests for data storage.

Feature: kia-paint-shop-iot-prototype
Property 7: Almacenamiento con TTL correcto
Property 8: Estructura de keys en DynamoDB

Tests that the system stores data with correct TTL and key structure.

Validates: Requirements 3.1, 3.2
"""

import sys
import time
from pathlib import Path
from datetime import datetime, timedelta

# Add lambdas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lambdas" / "ingest"))

from hypothesis import given, strategies as st, settings, assume
import pytest
from handler import calculate_ttl, build_dynamodb_item


# Feature: kia-paint-shop-iot-prototype, Property 7: Almacenamiento con TTL correcto
@settings(max_examples=100)
@given(
    days=st.integers(min_value=1, max_value=365)
)
def test_property_7_ttl_calculation_is_correct(days):
    """
    Property 7: Para cualquier dato almacenado en DynamoDB tabla sensor-data,
    el campo ttl debe ser igual al timestamp de creación más N días (en epoch seconds).
    
    **Validates: Requirements 3.1**
    """
    # Record the time before calculation
    before = datetime.utcnow()
    
    # Calculate TTL
    ttl = calculate_ttl(days)
    
    # Record the time after calculation
    after = datetime.utcnow()
    
    # Expected TTL range (accounting for execution time)
    expected_min = int((before + timedelta(days=days)).timestamp())
    expected_max = int((after + timedelta(days=days)).timestamp())
    
    # Property: TTL should be current time + days (within execution window)
    assert expected_min <= ttl <= expected_max, \
        f"TTL {ttl} not in expected range [{expected_min}, {expected_max}] for {days} days"


@settings(max_examples=100)
@given(
    days=st.integers(min_value=1, max_value=90)
)
def test_property_7_ttl_is_in_future(days):
    """
    Property 7: Para cualquier TTL calculado, debe ser un timestamp futuro
    (mayor que el timestamp actual).
    
    **Validates: Requirements 3.1**
    """
    # Calculate TTL
    ttl = calculate_ttl(days)
    
    # Current time in epoch seconds
    now = int(datetime.utcnow().timestamp())
    
    # Property: TTL must be in the future
    assert ttl > now, f"TTL {ttl} is not in the future (now: {now})"
    
    # Property: TTL should be at least 'days' worth of seconds in the future
    min_expected_ttl = now + (days * 24 * 60 * 60) - 60  # Allow 1 minute tolerance
    assert ttl >= min_expected_ttl, \
        f"TTL {ttl} is less than {days} days in the future (expected >= {min_expected_ttl})"


def test_property_7_default_ttl_is_30_days():
    """
    Property 7: Cuando no se especifica días, el TTL por defecto debe ser 30 días.
    
    **Validates: Requirements 3.1**
    """
    # Calculate TTL with default (30 days)
    ttl_default = calculate_ttl()
    
    # Calculate TTL with explicit 30 days
    ttl_explicit = calculate_ttl(30)
    
    # Property: Default should be same as explicit 30 days (within 1 second tolerance)
    assert abs(ttl_default - ttl_explicit) <= 1, \
        f"Default TTL {ttl_default} differs from explicit 30-day TTL {ttl_explicit}"


@settings(max_examples=100)
@given(
    days1=st.integers(min_value=1, max_value=90),
    days2=st.integers(min_value=1, max_value=90)
)
def test_property_7_ttl_ordering_is_consistent(days1, days2):
    """
    Property 7: Para cualquier par de TTLs calculados con diferentes días,
    el TTL con más días debe ser mayor.
    
    **Validates: Requirements 3.1**
    """
    # Assume days are different
    assume(days1 != days2)
    
    # Calculate TTLs
    ttl1 = calculate_ttl(days1)
    ttl2 = calculate_ttl(days2)
    
    # Property: More days should result in larger TTL
    if days1 > days2:
        assert ttl1 > ttl2, f"TTL for {days1} days ({ttl1}) should be > TTL for {days2} days ({ttl2})"
    else:
        assert ttl1 < ttl2, f"TTL for {days1} days ({ttl1}) should be < TTL for {days2} days ({ttl2})"


# Feature: kia-paint-shop-iot-prototype, Property 8: Estructura de keys en DynamoDB
@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_partition_key_format(variable_id, area, value, unit):
    """
    Property 8: Para cualquier item almacenado en sensor-data,
    la partition key (PK) debe tener formato "{area}#{variable_id}".
    
    **Validates: Requirements 3.2**
    """
    # Create message
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Expected PK format
    expected_pk = f"{area}#{variable_id}"
    
    # Property: PK must match expected format
    assert 'PK' in item, "Item missing PK field"
    assert item['PK'] == expected_pk, \
        f"PK '{item['PK']}' does not match expected format '{expected_pk}'"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_sort_key_format(variable_id, area, value, unit):
    """
    Property 8: Para cualquier item almacenado en sensor-data,
    la sort key (SK) debe tener formato "DATA#{timestamp_ms}" donde
    timestamp_ms es un número entero positivo.
    
    **Validates: Requirements 3.2**
    """
    # Create message with valid ISO 8601 timestamp
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Property: SK must exist and start with "DATA#"
    assert 'SK' in item, "Item missing SK field"
    assert item['SK'].startswith('DATA#'), \
        f"SK '{item['SK']}' does not start with 'DATA#'"
    
    # Property: SK must have format "DATA#{timestamp_ms}"
    sk_parts = item['SK'].split('#')
    assert len(sk_parts) == 2, f"SK '{item['SK']}' does not have format 'DATA#{{timestamp_ms}}'"
    assert sk_parts[0] == 'DATA', f"SK prefix is '{sk_parts[0]}', expected 'DATA'"
    
    # Property: timestamp_ms must be a positive integer
    timestamp_ms_str = sk_parts[1]
    assert timestamp_ms_str.isdigit(), \
        f"SK timestamp '{timestamp_ms_str}' is not a positive integer"
    
    timestamp_ms = int(timestamp_ms_str)
    assert timestamp_ms > 0, f"SK timestamp {timestamp_ms} is not positive"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_timestamp_ms_is_reasonable(variable_id, area, value, unit):
    """
    Property 8: Para cualquier item almacenado, el timestamp_ms en SK
    debe representar un tiempo razonable (no en el pasado distante ni futuro lejano).
    
    **Validates: Requirements 3.2**
    """
    # Create message
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Extract timestamp_ms from SK
    sk_parts = item['SK'].split('#')
    timestamp_ms = int(sk_parts[1])
    
    # Convert to seconds
    timestamp_s = timestamp_ms / 1000
    
    # Property: Timestamp should be reasonable (between 2020 and 2030)
    min_timestamp = datetime(2020, 1, 1).timestamp()
    max_timestamp = datetime(2030, 12, 31).timestamp()
    
    assert min_timestamp <= timestamp_s <= max_timestamp, \
        f"Timestamp {timestamp_s} is outside reasonable range [{min_timestamp}, {max_timestamp}]"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_item_contains_required_fields(variable_id, area, value, unit):
    """
    Property 8: Para cualquier item construido, debe contener todos los campos
    requeridos: PK, SK, variable_id, area, timestamp, value, unit, ttl.
    
    **Validates: Requirements 3.2**
    """
    # Create message
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Property: All required fields must be present
    required_fields = ['PK', 'SK', 'variable_id', 'area', 'timestamp', 'value', 'unit', 'ttl']
    
    for field in required_fields:
        assert field in item, f"Item missing required field: {field}"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_item_preserves_original_data(variable_id, area, value, unit):
    """
    Property 8: Para cualquier item construido, los campos de datos originales
    (variable_id, area, timestamp, value, unit) deben preservarse exactamente.
    
    **Validates: Requirements 3.2**
    """
    # Create message
    timestamp = '2024-01-15T10:30:00.000Z'
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': timestamp,
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Property: Original data must be preserved
    assert item['variable_id'] == variable_id, \
        f"variable_id changed from '{variable_id}' to '{item['variable_id']}'"
    assert item['area'] == area, \
        f"area changed from '{area}' to '{item['area']}'"
    assert item['timestamp'] == timestamp, \
        f"timestamp changed from '{timestamp}' to '{item['timestamp']}'"
    assert item['value'] == value, \
        f"value changed from {value} to {item['value']}"
    assert item['unit'] == unit, \
        f"unit changed from '{unit}' to '{item['unit']}'"


@settings(max_examples=100)
@given(
    variable_id=st.text(
        min_size=1, 
        max_size=50, 
        alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_'
    ).filter(lambda x: x and x.strip()),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_pk_contains_no_special_characters(variable_id, area, value, unit):
    """
    Property 8: Para cualquier PK generado con variable_id alfanumérico,
    debe contener solo caracteres alfanuméricos ASCII, guiones, y el delimitador '#'.
    
    **Validates: Requirements 3.2**
    """
    # Create message
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    pk = item['PK']
    
    # Property: PK should only contain safe ASCII characters
    # Allowed: ASCII alphanumeric, hyphen, underscore, and '#' delimiter
    import re
    pattern = r'^[a-zA-Z0-9\-_#]+$'
    
    assert re.match(pattern, pk), \
        f"PK '{pk}' contains invalid characters (allowed: ASCII alphanumeric, -, _, #)"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_pk_uniquely_identifies_variable(variable_id, area, value, unit):
    """
    Property 8: Para cualquier combinación única de (area, variable_id),
    el PK debe ser único y permitir identificar la variable.
    
    **Validates: Requirements 3.2**
    """
    # Create two messages with same variable_id and area
    message1 = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    message2 = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:31:00.000Z',  # Different timestamp
        'value': value + 1.0,  # Different value
        'unit': unit,
        'request_id': 'test-request-456',
        'processing_timestamp': '2024-01-15T10:31:01.000Z'
    }
    
    # Build DynamoDB items
    item1 = build_dynamodb_item(message1)
    item2 = build_dynamodb_item(message2)
    
    # Property: Same variable should have same PK
    assert item1['PK'] == item2['PK'], \
        f"Same variable should have same PK, got '{item1['PK']}' and '{item2['PK']}'"
    
    # Property: Different timestamps should have different SKs
    assert item1['SK'] != item2['SK'], \
        f"Different timestamps should have different SKs, both got '{item1['SK']}'"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_sk_allows_time_range_queries(variable_id, area, value, unit):
    """
    Property 8: Para cualquier conjunto de items con el mismo PK,
    los SKs deben ser ordenables lexicográficamente por tiempo.
    
    **Validates: Requirements 3.2**
    """
    # Create messages with different timestamps
    timestamps = [
        '2024-01-15T10:30:00.000Z',
        '2024-01-15T10:31:00.000Z',
        '2024-01-15T10:32:00.000Z',
    ]
    
    items = []
    for ts in timestamps:
        message = {
            'variable_id': variable_id,
            'area': area,
            'timestamp': ts,
            'value': value,
            'unit': unit,
            'request_id': 'test-request-123',
            'processing_timestamp': '2024-01-15T10:30:01.000Z'
        }
        items.append(build_dynamodb_item(message))
    
    # Property: SKs should be in ascending order
    sks = [item['SK'] for item in items]
    sorted_sks = sorted(sks)
    
    assert sks == sorted_sks, \
        f"SKs are not in chronological order: {sks} vs {sorted_sks}"


@settings(max_examples=100)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=500.0, allow_nan=False, allow_infinity=False),
)
def test_property_8_metadata_is_preserved(variable_id, area, value, unit, min_range, max_range):
    """
    Property 8: Para cualquier mensaje con metadata, el item DynamoDB
    debe preservar la metadata completa.
    
    **Validates: Requirements 3.2**
    """
    # Create message with metadata
    metadata = {
        'min_range': min_range,
        'max_range': max_range,
        'alarm_low': min_range + 10.0,
        'alarm_high': max_range - 10.0
    }
    
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'metadata': metadata,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Property: Metadata must be preserved
    assert 'metadata' in item, "Item missing metadata field"
    assert item['metadata'] == metadata, \
        f"Metadata not preserved: expected {metadata}, got {item['metadata']}"


@settings(max_examples=50)
@given(
    variable_id=st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'), 
        whitelist_characters='-_'
    )),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    unit=st.text(min_size=1, max_size=20).filter(lambda x: x.strip()),
)
def test_property_8_quality_defaults_to_good(variable_id, area, value, unit):
    """
    Property 8: Para cualquier mensaje sin campo 'quality',
    el item DynamoDB debe tener quality='good' por defecto.
    
    **Validates: Requirements 3.2**
    """
    # Create message without quality field
    message = {
        'variable_id': variable_id,
        'area': area,
        'timestamp': '2024-01-15T10:30:00.000Z',
        'value': value,
        'unit': unit,
        'request_id': 'test-request-123',
        'processing_timestamp': '2024-01-15T10:30:01.000Z'
    }
    
    # Build DynamoDB item
    item = build_dynamodb_item(message)
    
    # Property: Quality should default to 'good'
    assert 'quality' in item, "Item missing quality field"
    assert item['quality'] == 'good', \
        f"Quality should default to 'good', got '{item['quality']}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
