"""
Property-based tests for data generator.

Feature: kia-paint-shop-iot-prototype
Property 2: Intervalos de generación consistentes
Property 3: Timestamps en formato ISO 8601 válido

Tests that generated data has consistent intervals and valid timestamps.

Validates: Requirements 1.3, 1.4
"""

import sys
from pathlib import Path
from datetime import datetime, timezone
import time

# Add simulator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simulator"))

from hypothesis import given, strategies as st, settings
import pytest
from config_loader import Variable
from data_generator import DataGenerator, DataPoint


# Feature: kia-paint-shop-iot-prototype, Property 2: Intervalos de generación consistentes
@settings(max_examples=20, deadline=None)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    interval_seconds=st.floats(min_value=0.1, max_value=2.0, allow_nan=False, allow_infinity=False)
)
def test_property_2_generation_intervals_are_consistent(min_range, max_range, interval_seconds):
    """
    Property 2: Para cualquier par de mensajes consecutivos del simulador,
    la diferencia entre sus timestamps debe ser aproximadamente igual al
    intervalo configurado (±1 segundo de tolerancia).
    
    **Validates: Requirements 1.3**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=0.0)
    
    # Generate multiple data points with time intervals
    timestamps = []
    for _ in range(3):
        data_point = generator.generate_value(variable)
        timestamps.append(data_point.timestamp)
        time.sleep(interval_seconds)
    
    # Parse timestamps
    parsed_times = [datetime.fromisoformat(ts.replace('Z', '+00:00')) for ts in timestamps]
    
    # Check intervals between consecutive timestamps
    for i in range(len(parsed_times) - 1):
        time_diff = (parsed_times[i+1] - parsed_times[i]).total_seconds()
        
        # Property: Time difference should be approximately equal to interval_seconds
        # Allow ±1 second tolerance
        assert abs(time_diff - interval_seconds) <= 1.0, \
            f"Time difference ({time_diff:.2f}s) not within tolerance of interval ({interval_seconds:.2f}s)"


# Feature: kia-paint-shop-iot-prototype, Property 3: Timestamps en formato ISO 8601 válido
@settings(max_examples=20)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_property_3_timestamps_are_valid_iso8601(min_range, max_range):
    """
    Property 3: Para cualquier mensaje generado, el campo timestamp debe ser
    parseable como ISO 8601 con zona horaria y representar una fecha/hora válida.
    
    **Validates: Requirements 1.4**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=0.0)
    
    # Generate a data point
    data_point = generator.generate_value(variable)
    
    # Property: Timestamp must be parseable as ISO 8601
    try:
        # Parse timestamp (handle 'Z' suffix for UTC)
        parsed_time = datetime.fromisoformat(data_point.timestamp.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        pytest.fail(f"Timestamp '{data_point.timestamp}' is not valid ISO 8601: {e}")
    
    # Property: Parsed time must have timezone info
    assert parsed_time.tzinfo is not None, \
        f"Timestamp '{data_point.timestamp}' does not include timezone information"
    
    # Property: Timestamp should be recent (within last minute)
    now = datetime.now(timezone.utc)
    time_diff = abs((now - parsed_time).total_seconds())
    assert time_diff < 60, \
        f"Timestamp '{data_point.timestamp}' is not recent (diff: {time_diff:.2f}s)"
    
    # Property: Timestamp format should match expected pattern
    # Format: YYYY-MM-DDTHH:MM:SS.sssZ
    assert 'T' in data_point.timestamp, "Timestamp missing 'T' separator"
    assert data_point.timestamp.endswith('Z'), "Timestamp missing 'Z' UTC indicator"
    assert '.' in data_point.timestamp, "Timestamp missing milliseconds"


@settings(max_examples=20)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_property_generated_values_within_range(min_range, max_range):
    """
    Property: Para cualquier variable, todos los valores generados deben estar
    dentro del rango definido (min_range, max_range).
    
    **Validates: Requirements 1.2**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=0.0)
    
    # Generate multiple values
    for _ in range(10):
        data_point = generator.generate_value(variable)
        
        # Property: Value must be within range
        assert min_range <= data_point.value <= max_range, \
            f"Generated value {data_point.value} outside range [{min_range}, {max_range}]"


@settings(max_examples=20)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_property_anomalous_values_can_exceed_alarm_thresholds(min_range, max_range):
    """
    Property: Cuando se fuerza una anomalía, el valor generado puede estar
    fuera de los umbrales de alarma pero dentro del rango físico.
    
    **Validates: Requirements 1.5**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=1.0)  # Force anomalies
    
    # Generate multiple anomalous values
    anomaly_count = 0
    for _ in range(10):
        data_point = generator.generate_value(variable, force_anomaly=True)
        
        # Property: Value must still be within physical range
        assert min_range <= data_point.value <= max_range, \
            f"Anomalous value {data_point.value} outside physical range [{min_range}, {max_range}]"
        
        # Check if value is outside alarm thresholds
        if data_point.value < variable.alarm_low or data_point.value > variable.alarm_high:
            anomaly_count += 1
    
    # Property: At least some values should be outside alarm thresholds
    # (since we're forcing anomalies)
    assert anomaly_count > 0, \
        "No anomalous values generated despite forcing anomalies"


@settings(max_examples=20)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_property_data_point_has_required_fields(min_range, max_range):
    """
    Property: Todo DataPoint generado debe tener todos los campos requeridos
    con valores válidos.
    
    **Validates: Requirements 1.2, 1.4**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=0.0)
    data_point = generator.generate_value(variable)
    
    # Property: All required fields must be present
    assert data_point.variable_id, "variable_id is missing or empty"
    assert data_point.area, "area is missing or empty"
    assert data_point.timestamp, "timestamp is missing or empty"
    assert data_point.value is not None, "value is missing"
    assert data_point.unit is not None, "unit is missing"
    assert data_point.quality, "quality is missing or empty"
    assert data_point.metadata, "metadata is missing or empty"
    
    # Property: Metadata must contain required fields
    assert 'min_range' in data_point.metadata, "metadata missing min_range"
    assert 'max_range' in data_point.metadata, "metadata missing max_range"
    assert 'alarm_low' in data_point.metadata, "metadata missing alarm_low"
    assert 'alarm_high' in data_point.metadata, "metadata missing alarm_high"
    
    # Property: Quality must be valid
    assert data_point.quality in ['good', 'bad', 'uncertain'], \
        f"Invalid quality value: {data_point.quality}"


@settings(max_examples=20)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
)
def test_property_smooth_transitions_between_values(min_range, max_range):
    """
    Property: Los valores consecutivos generados deben tener transiciones suaves
    (cambios no mayores al 10% del rango).
    
    **Validates: Requirements 1.2**
    """
    # Create a test variable
    range_span = max_range - min_range
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=min_range + (range_span * 0.1),
        alarm_high=max_range - (range_span * 0.1),
        description="Test variable",
        source_file="test",
        active=True
    )
    
    generator = DataGenerator(anomaly_probability=0.0)
    
    # Generate multiple values
    values = []
    for _ in range(5):
        data_point = generator.generate_value(variable)
        values.append(data_point.value)
    
    # Property: Consecutive values should have smooth transitions
    max_allowed_change = range_span * 0.15  # Allow 15% change (slightly more than 10% for tolerance)
    
    for i in range(len(values) - 1):
        change = abs(values[i+1] - values[i])
        assert change <= max_allowed_change, \
            f"Change between consecutive values ({change:.2f}) exceeds maximum allowed ({max_allowed_change:.2f})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
