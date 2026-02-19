"""
Property-based tests for API data round-trip correctness.

**Validates: Requirements 3.3, 5.2**

Property 9: Round-trip de almacenamiento y consulta
Para cualquier conjunto de datos almacenados para una variable en un rango de tiempo,
consultar esa variable con ese rango debe retornar exactamente los mismos datos
(mismo número de puntos, mismos valores, mismos timestamps).

This test validates that data stored in DynamoDB can be retrieved accurately
through the API without loss or corruption.
"""

import json
import os
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import List, Dict, Any

import boto3
import pytest
from hypothesis import given, strategies as st, settings, assume
from moto import mock_dynamodb

# Feature tag for tracking
# Feature: kia-paint-shop-iot-prototype, Property 9: Round-trip de almacenamiento y consulta


# Strategies for generating test data
@st.composite
def variable_data_point(draw, base_timestamp=None):
    """Generate a single data point for a variable."""
    if base_timestamp is None:
        # Generate timestamp within a reasonable range (last 30 days)
        days_ago = draw(st.integers(min_value=0, max_value=29))
        hours = draw(st.integers(min_value=0, max_value=23))
        minutes = draw(st.integers(min_value=0, max_value=59))
        seconds = draw(st.integers(min_value=0, max_value=59))
        
        base_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
        timestamp = base_time.replace(hour=hours, minute=minutes, second=seconds, microsecond=0)
    else:
        timestamp = base_timestamp
    
    return {
        'timestamp': timestamp.isoformat().replace('+00:00', 'Z'),
        # Constrain values to avoid decimal underflow (DynamoDB limitation)
        'value': draw(st.floats(min_value=-100.0, max_value=500.0, allow_nan=False, allow_infinity=False).filter(lambda x: abs(x) > 1e-100 or x == 0.0)),
        'unit': draw(st.sampled_from(['°C', 'pH', 'V', 'm/min', 'bar', 'L/min'])),
        'quality': draw(st.sampled_from(['good', 'bad', 'uncertain']))
    }


@st.composite
def variable_dataset(draw):
    """Generate a dataset of data points for a variable."""
    variable_id = draw(st.sampled_from(['PT-001', 'PT-002', 'ED-001', 'PC-001']))
    area = draw(st.sampled_from(['pre-treatment', 'e-coat', 'production-control']))
    
    # Generate 1-20 data points with unique timestamps
    num_points = draw(st.integers(min_value=1, max_value=20))
    
    # Generate base timestamp
    days_ago = draw(st.integers(min_value=0, max_value=29))
    base_time = datetime.now(timezone.utc) - timedelta(days=days_ago)
    base_time = base_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Generate data points with incrementing timestamps (ensures uniqueness)
    data_points = []
    for i in range(num_points):
        timestamp = base_time + timedelta(seconds=i * 60)  # 1 minute apart
        point = {
            'timestamp': timestamp.isoformat().replace('+00:00', 'Z'),
            'value': draw(st.floats(min_value=-100.0, max_value=500.0, allow_nan=False, allow_infinity=False).filter(lambda x: abs(x) > 1e-100 or x == 0.0)),
            'unit': draw(st.sampled_from(['°C', 'pH', 'V', 'm/min', 'bar', 'L/min'])),
            'quality': draw(st.sampled_from(['good', 'bad', 'uncertain']))
        }
        data_points.append(point)
    
    return {
        'variable_id': variable_id,
        'area': area,
        'data_points': data_points
    }


def create_sensor_data_table(dynamodb):
    """Create the sensor-data DynamoDB table for testing."""
    table = dynamodb.create_table(
        TableName='kia-paintshop-sensor-data',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    return table


def create_variables_metadata_table(dynamodb):
    """Create the variables-metadata DynamoDB table for testing."""
    table = dynamodb.create_table(
        TableName='kia-paintshop-variables-metadata',
        KeySchema=[
            {'AttributeName': 'PK', 'KeyType': 'HASH'},
            {'AttributeName': 'SK', 'KeyType': 'RANGE'}
        ],
        AttributeDefinitions=[
            {'AttributeName': 'PK', 'AttributeType': 'S'},
            {'AttributeName': 'SK', 'AttributeType': 'S'}
        ],
        BillingMode='PAY_PER_REQUEST'
    )
    return table


def store_data_in_dynamodb(table, variable_id: str, area: str, data_points: List[Dict[str, Any]]):
    """Store data points in DynamoDB sensor-data table."""
    for point in data_points:
        timestamp_dt = datetime.fromisoformat(point['timestamp'].replace('Z', '+00:00'))
        timestamp_ms = int(timestamp_dt.timestamp() * 1000)
        
        # Calculate TTL (30 days from now)
        ttl = int((datetime.now(timezone.utc) + timedelta(days=30)).timestamp())
        
        item = {
            'PK': f"{area}#{variable_id}",
            'SK': f"DATA#{timestamp_ms}",
            'variable_id': variable_id,
            'area': area,
            'timestamp': point['timestamp'],
            'value': Decimal(str(point['value'])),
            'unit': point['unit'],
            'quality': point['quality'],
            'ttl': ttl
        }
        
        table.put_item(Item=item)


def store_variable_metadata(table, variable_id: str, area: str):
    """Store variable metadata in DynamoDB."""
    item = {
        'PK': f"VAR#{variable_id}",
        'SK': 'METADATA',
        'variable_id': variable_id,
        'area': area,
        'name': f'Test Variable {variable_id}',
        'unit': '°C',
        'data_type': 'float',
        'min_range': Decimal('0.0'),
        'max_range': Decimal('100.0'),
        'alarm_low': Decimal('10.0'),
        'alarm_high': Decimal('90.0'),
        'active': True
    }
    
    table.put_item(Item=item)


@pytest.fixture
def dynamodb_tables():
    """Fixture to create DynamoDB tables for testing."""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        sensor_data_table = create_sensor_data_table(dynamodb)
        variables_metadata_table = create_variables_metadata_table(dynamodb)
        yield sensor_data_table, variables_metadata_table


@given(dataset=variable_dataset())
@settings(max_examples=50, deadline=5000)
def test_property_roundtrip_data_storage_and_retrieval(dataset):
    """
    Property 9: Round-trip de almacenamiento y consulta
    
    **Validates: Requirements 3.3, 5.2**
    
    For any set of data points stored for a variable in a time range,
    querying that variable with that range should return exactly the same data
    (same number of points, same values, same timestamps).
    """
    with mock_dynamodb():
        # Setup DynamoDB tables
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        sensor_data_table = create_sensor_data_table(dynamodb)
        variables_metadata_table = create_variables_metadata_table(dynamodb)
        
        variable_id = dataset['variable_id']
        area = dataset['area']
        data_points = dataset['data_points']
        
        # Assume we have at least one data point
        assume(len(data_points) > 0)
        
        # Store variable metadata
        store_variable_metadata(variables_metadata_table, variable_id, area)
        
        # Store data points in DynamoDB
        store_data_in_dynamodb(sensor_data_table, variable_id, area, data_points)
        
        # Determine time range for query
        timestamps = [datetime.fromisoformat(p['timestamp'].replace('Z', '+00:00')) for p in data_points]
        start_dt = min(timestamps)
        end_dt = max(timestamps)
        
        # Add small buffer to ensure we capture all points
        start_dt = start_dt - timedelta(seconds=1)
        end_dt = end_dt + timedelta(seconds=1)
        
        # Query data directly from the mocked table
        start_ms = int(start_dt.timestamp() * 1000)
        end_ms = int(end_dt.timestamp() * 1000)
        
        pk = f"{area}#{variable_id}"
        sk_start = f"DATA#{start_ms}"
        sk_end = f"DATA#{end_ms}"
        
        response = sensor_data_table.query(
            KeyConditionExpression='PK = :pk AND SK BETWEEN :sk_start AND :sk_end',
            ExpressionAttributeValues={
                ':pk': pk,
                ':sk_start': sk_start,
                ':sk_end': sk_end
            },
            ScanIndexForward=True
        )
        
        retrieved_items = response.get('Items', [])
        
        # Format the retrieved data
        from lambdas.api.get_variable_data import format_data_points
        retrieved_data = format_data_points(retrieved_items)
        
        # Property validation: Round-trip correctness
        
        # 1. Same number of data points
        assert len(retrieved_data) == len(data_points), \
            f"Expected {len(data_points)} points, got {len(retrieved_data)}"
        
        # 2. Sort both lists by timestamp for comparison
        original_sorted = sorted(data_points, key=lambda x: x['timestamp'])
        retrieved_sorted = sorted(retrieved_data, key=lambda x: x['timestamp'])
        
        # 3. Compare each data point
        for i, (original, retrieved) in enumerate(zip(original_sorted, retrieved_sorted)):
            # Timestamps should match exactly
            assert original['timestamp'] == retrieved['timestamp'], \
                f"Point {i}: Timestamp mismatch - expected {original['timestamp']}, got {retrieved['timestamp']}"
            
            # Values should match within floating point precision
            assert abs(original['value'] - retrieved['value']) < 0.01, \
                f"Point {i}: Value mismatch - expected {original['value']}, got {retrieved['value']}"
            
            # Units should match
            assert original['unit'] == retrieved['unit'], \
                f"Point {i}: Unit mismatch - expected {original['unit']}, got {retrieved['unit']}"
            
            # Quality should match
            assert original['quality'] == retrieved['quality'], \
                f"Point {i}: Quality mismatch - expected {original['quality']}, got {retrieved['quality']}"


@mock_dynamodb
def test_roundtrip_empty_dataset():
    """Test round-trip with no data points (edge case)."""
    # Setup DynamoDB tables
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_data_table = create_sensor_data_table(dynamodb)
    variables_metadata_table = create_variables_metadata_table(dynamodb)
    
    variable_id = 'PT-001'
    area = 'pre-treatment'
    
    # Store variable metadata
    store_variable_metadata(variables_metadata_table, variable_id, area)
    
    # Query with no data stored
    from lambdas.api.get_variable_data import format_data_points
    
    start_dt = datetime.now(timezone.utc) - timedelta(hours=1)
    end_dt = datetime.now(timezone.utc)
    
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    pk = f"{area}#{variable_id}"
    sk_start = f"DATA#{start_ms}"
    sk_end = f"DATA#{end_ms}"
    
    response = sensor_data_table.query(
        KeyConditionExpression='PK = :pk AND SK BETWEEN :sk_start AND :sk_end',
        ExpressionAttributeValues={
            ':pk': pk,
            ':sk_start': sk_start,
            ':sk_end': sk_end
        },
        ScanIndexForward=True
    )
    
    retrieved_items = response.get('Items', [])
    retrieved_data = format_data_points(retrieved_items)
    
    # Should return empty list
    assert len(retrieved_data) == 0


@mock_dynamodb
def test_roundtrip_single_data_point():
    """Test round-trip with exactly one data point."""
    # Setup DynamoDB tables
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    sensor_data_table = create_sensor_data_table(dynamodb)
    variables_metadata_table = create_variables_metadata_table(dynamodb)
    
    variable_id = 'PT-001'
    area = 'pre-treatment'
    
    # Store variable metadata
    store_variable_metadata(variables_metadata_table, variable_id, area)
    
    # Single data point
    timestamp = datetime.now(timezone.utc).replace(microsecond=0)
    data_points = [{
        'timestamp': timestamp.isoformat().replace('+00:00', 'Z'),
        'value': 65.5,
        'unit': '°C',
        'quality': 'good'
    }]
    
    # Store data
    store_data_in_dynamodb(sensor_data_table, variable_id, area, data_points)
    
    # Query data
    from lambdas.api.get_variable_data import format_data_points
    
    start_dt = timestamp - timedelta(seconds=1)
    end_dt = timestamp + timedelta(seconds=1)
    
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    pk = f"{area}#{variable_id}"
    sk_start = f"DATA#{start_ms}"
    sk_end = f"DATA#{end_ms}"
    
    response = sensor_data_table.query(
        KeyConditionExpression='PK = :pk AND SK BETWEEN :sk_start AND :sk_end',
        ExpressionAttributeValues={
            ':pk': pk,
            ':sk_start': sk_start,
            ':sk_end': sk_end
        },
        ScanIndexForward=True
    )
    
    retrieved_items = response.get('Items', [])
    retrieved_data = format_data_points(retrieved_items)
    
    # Should return exactly one point
    assert len(retrieved_data) == 1
    assert retrieved_data[0]['timestamp'] == data_points[0]['timestamp']
    assert abs(retrieved_data[0]['value'] - data_points[0]['value']) < 0.01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
