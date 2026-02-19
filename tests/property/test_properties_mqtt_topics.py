"""
Property-based tests for MQTT topic structure.

Feature: kia-paint-shop-iot-prototype
Property 5: Estructura de topics MQTT jerárquica

Tests that all MQTT topics follow the hierarchical structure:
kia/paintshop/{area}/{variable_id}

Validates: Requirements 2.2
"""

import sys
from pathlib import Path
import re

# Add simulator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simulator"))

from hypothesis import given, strategies as st, settings
import pytest
from config_loader import Variable
from data_generator import DataGenerator, DataPoint
from mqtt_publisher import MQTTPublisher, MQTTConfig


# Feature: kia-paint-shop-iot-prototype, Property 5: Estructura de topics MQTT jerárquica
@settings(max_examples=100)
@given(
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    variable_id=st.text(
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
        min_size=5,
        max_size=20
    ).filter(lambda x: x and not x.startswith('-') and not x.endswith('-'))
)
def test_property_5_topic_structure_is_hierarchical(area, variable_id):
    """
    Property 5: Para cualquier mensaje publicado a IoT Core, el topic debe
    seguir el patrón kia/paintshop/{area}/{variable_id} donde area es uno de
    [pre-treatment, e-coat, production-control] y variable_id es un ID válido.
    
    **Validates: Requirements 2.2**
    """
    # Create MQTT config with default topic prefix
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix="kia/paintshop"
    )
    
    # Create publisher (without connecting)
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Build topic using the internal method
    topic = publisher._build_topic(area, variable_id)
    
    # Property: Topic must follow the hierarchical pattern
    expected_pattern = r'^kia/paintshop/(pre-treatment|e-coat|production-control)/[A-Z0-9\-]+$'
    assert re.match(expected_pattern, topic), \
        f"Topic '{topic}' does not match expected pattern '{expected_pattern}'"
    
    # Property: Topic must have exactly 4 levels
    topic_parts = topic.split('/')
    assert len(topic_parts) == 4, \
        f"Topic '{topic}' must have 4 levels, got {len(topic_parts)}"
    
    # Property: First level must be 'kia'
    assert topic_parts[0] == 'kia', \
        f"First level must be 'kia', got '{topic_parts[0]}'"
    
    # Property: Second level must be 'paintshop'
    assert topic_parts[1] == 'paintshop', \
        f"Second level must be 'paintshop', got '{topic_parts[1]}'"
    
    # Property: Third level must be the area
    assert topic_parts[2] == area, \
        f"Third level must be '{area}', got '{topic_parts[2]}'"
    
    # Property: Fourth level must be the variable_id
    assert topic_parts[3] == variable_id, \
        f"Fourth level must be '{variable_id}', got '{topic_parts[3]}'"
    
    # Property: Area must be one of the valid areas
    valid_areas = ['pre-treatment', 'e-coat', 'production-control']
    assert topic_parts[2] in valid_areas, \
        f"Area '{topic_parts[2]}' must be one of {valid_areas}"


@settings(max_examples=100)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control'])
)
def test_property_5_data_point_generates_valid_topic(min_range, max_range, area):
    """
    Property 5: Para cualquier DataPoint generado, el topic construido a partir
    de sus campos area y variable_id debe ser válido según el patrón jerárquico.
    
    **Validates: Requirements 2.2**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id=f"{area.upper()[:2]}-TEST-001",
        name="Test Variable",
        area=area,
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    # Generate a data point
    generator = DataGenerator(anomaly_probability=0.0)
    data_point = generator.generate_value(variable)
    
    # Create MQTT config
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix="kia/paintshop"
    )
    
    # Create publisher
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Build topic from data point
    topic = publisher._build_topic(data_point.area, data_point.variable_id)
    
    # Property: Topic must be valid
    expected_pattern = r'^kia/paintshop/(pre-treatment|e-coat|production-control)/[A-Z0-9\-]+$'
    assert re.match(expected_pattern, topic), \
        f"Topic '{topic}' does not match expected pattern"
    
    # Property: Topic must contain the data point's area
    assert f"/{data_point.area}/" in topic, \
        f"Topic '{topic}' must contain area '{data_point.area}'"
    
    # Property: Topic must end with the variable_id
    assert topic.endswith(data_point.variable_id), \
        f"Topic '{topic}' must end with variable_id '{data_point.variable_id}'"


def test_property_5_all_loaded_variables_generate_valid_topics():
    """
    Property 5: Para todas las variables cargadas desde CSV, los topics
    generados deben seguir el patrón jerárquico válido.
    
    **Validates: Requirements 2.2**
    """
    from config_loader import ConfigLoader
    
    # Load all variables
    loader = ConfigLoader(base_path=Path(__file__).parent.parent.parent / "simulator")
    
    try:
        variables = loader.load_all()
    except FileNotFoundError:
        pytest.skip("CSV files not found - skipping test")
        return
    
    # Create MQTT config
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix="kia/paintshop"
    )
    
    # Create publisher
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Property: All variables must generate valid topics
    expected_pattern = r'^kia/paintshop/(pre-treatment|e-coat|production-control)/[A-Z0-9\-]+$'
    
    for var_id, variable in variables.items():
        topic = publisher._build_topic(variable.area, variable.variable_id)
        
        # Check pattern
        assert re.match(expected_pattern, topic), \
            f"Variable {var_id}: Topic '{topic}' does not match expected pattern"
        
        # Check structure
        topic_parts = topic.split('/')
        assert len(topic_parts) == 4, \
            f"Variable {var_id}: Topic must have 4 levels, got {len(topic_parts)}"
        
        assert topic_parts[0] == 'kia', \
            f"Variable {var_id}: First level must be 'kia'"
        
        assert topic_parts[1] == 'paintshop', \
            f"Variable {var_id}: Second level must be 'paintshop'"
        
        assert topic_parts[2] == variable.area, \
            f"Variable {var_id}: Third level must be '{variable.area}', got '{topic_parts[2]}'"
        
        assert topic_parts[3] == variable.variable_id, \
            f"Variable {var_id}: Fourth level must be '{variable.variable_id}', got '{topic_parts[3]}'"


@settings(max_examples=100)
@given(
    topic_prefix=st.sampled_from(['kia/paintshop', 'test/paintshop', 'kia/test']),
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    variable_id=st.text(
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
        min_size=5,
        max_size=20
    ).filter(lambda x: x and not x.startswith('-') and not x.endswith('-'))
)
def test_property_5_topic_prefix_is_configurable(topic_prefix, area, variable_id):
    """
    Property 5: El prefijo del topic debe ser configurable, pero la estructura
    jerárquica {prefix}/{area}/{variable_id} debe mantenerse.
    
    **Validates: Requirements 2.2**
    """
    # Create MQTT config with custom topic prefix
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix=topic_prefix
    )
    
    # Create publisher
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Build topic
    topic = publisher._build_topic(area, variable_id)
    
    # Property: Topic must start with the configured prefix
    assert topic.startswith(topic_prefix), \
        f"Topic '{topic}' must start with prefix '{topic_prefix}'"
    
    # Property: Topic must have the hierarchical structure
    expected_topic = f"{topic_prefix}/{area}/{variable_id}"
    assert topic == expected_topic, \
        f"Topic '{topic}' must match expected '{expected_topic}'"
    
    # Property: Topic must contain the area
    assert f"/{area}/" in topic, \
        f"Topic '{topic}' must contain area '{area}'"
    
    # Property: Topic must end with variable_id
    assert topic.endswith(variable_id), \
        f"Topic '{topic}' must end with variable_id '{variable_id}'"


@settings(max_examples=100)
@given(
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control'])
)
def test_property_5_topics_are_unique_per_variable(area):
    """
    Property 5: Cada variable debe tener un topic único. No debe haber
    colisiones de topics entre diferentes variables.
    
    **Validates: Requirements 2.2**
    """
    from config_loader import ConfigLoader
    
    # Load all variables
    loader = ConfigLoader(base_path=Path(__file__).parent.parent.parent / "simulator")
    
    try:
        loader.load_all()
    except FileNotFoundError:
        pytest.skip("CSV files not found - skipping test")
        return
    
    # Get variables for the specified area
    area_vars = loader.get_variables_by_area(area)
    
    # Create MQTT config
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix="kia/paintshop"
    )
    
    # Create publisher
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Generate topics for all variables in the area
    topics = set()
    for variable in area_vars:
        topic = publisher._build_topic(variable.area, variable.variable_id)
        
        # Property: Topic must be unique (no duplicates)
        assert topic not in topics, \
            f"Duplicate topic found: '{topic}' for variable {variable.variable_id}"
        
        topics.add(topic)
    
    # Property: Number of unique topics must equal number of variables
    assert len(topics) == len(area_vars), \
        f"Expected {len(area_vars)} unique topics, got {len(topics)}"


@settings(max_examples=100)
@given(
    area=st.sampled_from(['pre-treatment', 'e-coat', 'production-control']),
    variable_id=st.text(
        alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-',
        min_size=5,
        max_size=20
    ).filter(lambda x: x and not x.startswith('-') and not x.endswith('-'))
)
def test_property_5_topics_do_not_contain_invalid_characters(area, variable_id):
    """
    Property 5: Los topics MQTT no deben contener caracteres inválidos
    (espacios, caracteres especiales excepto guiones).
    
    **Validates: Requirements 2.2**
    """
    # Create MQTT config
    mqtt_config = MQTTConfig(
        endpoint="test.iot.us-east-1.amazonaws.com",
        port=8883,
        cert_path="certs/device.crt",
        key_path="certs/device.key",
        ca_path="certs/AmazonRootCA1.pem",
        client_id="test-client",
        topic_prefix="kia/paintshop"
    )
    
    # Create publisher
    publisher = MQTTPublisher(config=mqtt_config)
    
    # Build topic
    topic = publisher._build_topic(area, variable_id)
    
    # Property: Topic must not contain spaces
    assert ' ' not in topic, \
        f"Topic '{topic}' must not contain spaces"
    
    # Property: Topic must not contain invalid MQTT characters
    # MQTT allows: alphanumeric, /, -, _
    # We use: alphanumeric, /, -
    invalid_chars = ['#', '+', '$', '*', '?', '!', '@', '%', '^', '&', '(', ')', '=', '[', ']', '{', '}', '\\', '|', ';', ':', '"', "'", '<', '>', ',', '.', '~', '`']
    for char in invalid_chars:
        assert char not in topic, \
            f"Topic '{topic}' must not contain invalid character '{char}'"
    
    # Property: Topic must only contain allowed characters
    # Allowed: a-z, A-Z, 0-9, /, -
    allowed_pattern = r'^[a-zA-Z0-9/\-]+$'
    assert re.match(allowed_pattern, topic), \
        f"Topic '{topic}' contains invalid characters (allowed: a-z, A-Z, 0-9, /, -)"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
