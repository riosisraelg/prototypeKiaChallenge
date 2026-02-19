"""
Property-based tests for alarm generation.

Feature: kia-paint-shop-iot-prototype
Property 4: Generación de alarmas por exceso de umbrales

Tests that alarms are correctly generated when values exceed thresholds,
and that severity is calculated based on the percentage of exceedance.

Validates: Requirements 1.5, 4.2
"""

import sys
from pathlib import Path

# Add simulator to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simulator"))

from hypothesis import given, strategies as st, settings, assume
import pytest
from config_loader import Variable
from data_generator import DataPoint
from alarm_simulator import AlarmSimulator, AlarmSeverity


# Feature: kia-paint-shop-iot-prototype, Property 4: Generación de alarmas por exceso de umbrales
@settings(max_examples=200)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    value_below_low=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False)
)
def test_property_4_low_alarm_triggers_when_below_threshold(min_range, max_range, value_below_low):
    """
    Property 4: Para cualquier valor que esté por debajo del umbral alarm_low,
    se debe generar una alarma de tipo "low".
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable with alarm thresholds
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.1)
    alarm_high = max_range - (range_span * 0.1)
    
    # Ensure value is below alarm_low
    value = alarm_low - abs(value_below_low) - 0.01
    assume(value >= min_range - 100)  # Keep value reasonable
    
    variable = Variable(
        variable_id="TEST-001",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-001",
        area="pre-treatment",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: Alarm must be triggered
    assert alarm_info.is_alarm is True, \
        f"Alarm should trigger when value {value} < alarm_low {alarm_low}"
    
    # Property: Alarm type must be "low"
    assert alarm_info.threshold_type == "low", \
        f"Alarm type should be 'low' when value is below threshold"
    
    # Property: Threshold value must match alarm_low
    assert alarm_info.threshold_value == alarm_low, \
        f"Threshold value should be {alarm_low}, got {alarm_info.threshold_value}"


@settings(max_examples=200)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    value_above_high=st.floats(min_value=0.1, max_value=100.0, allow_nan=False, allow_infinity=False)
)
def test_property_4_high_alarm_triggers_when_above_threshold(min_range, max_range, value_above_high):
    """
    Property 4: Para cualquier valor que esté por encima del umbral alarm_high,
    se debe generar una alarma de tipo "high".
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable with alarm thresholds
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.1)
    alarm_high = max_range - (range_span * 0.1)
    
    # Ensure value is above alarm_high
    value = alarm_high + abs(value_above_high) + 0.01
    assume(value <= max_range + 100)  # Keep value reasonable
    
    variable = Variable(
        variable_id="TEST-002",
        name="Test Variable",
        area="e-coat",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-002",
        area="e-coat",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: Alarm must be triggered
    assert alarm_info.is_alarm is True, \
        f"Alarm should trigger when value {value} > alarm_high {alarm_high}"
    
    # Property: Alarm type must be "high"
    assert alarm_info.threshold_type == "high", \
        f"Alarm type should be 'high' when value is above threshold"
    
    # Property: Threshold value must match alarm_high
    assert alarm_info.threshold_value == alarm_high, \
        f"Threshold value should be {alarm_high}, got {alarm_info.threshold_value}"


@settings(max_examples=200)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    value_offset=st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
)
def test_property_4_no_alarm_within_thresholds(min_range, max_range, value_offset):
    """
    Property 4: Para cualquier valor que esté dentro de los umbrales
    [alarm_low, alarm_high], NO se debe generar alarma.
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable with alarm thresholds
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.1)
    alarm_high = max_range - (range_span * 0.1)
    
    # Generate value within thresholds
    alarm_range = alarm_high - alarm_low
    value = alarm_low + (alarm_range * value_offset)
    
    variable = Variable(
        variable_id="TEST-003",
        name="Test Variable",
        area="production-control",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-003",
        area="production-control",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: No alarm should be triggered
    assert alarm_info.is_alarm is False, \
        f"No alarm should trigger when value {value} is within [{alarm_low}, {alarm_high}]"
    
    # Property: Severity should be None
    assert alarm_info.severity is None, \
        f"Severity should be None when no alarm"
    
    # Property: Threshold type should be None
    assert alarm_info.threshold_type is None, \
        f"Threshold type should be None when no alarm"


@settings(max_examples=200)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    exceedance_factor=st.floats(min_value=0.0, max_value=0.09, allow_nan=False, allow_infinity=False)
)
def test_property_4_warning_severity_below_10_percent(min_range, max_range, exceedance_factor):
    """
    Property 4: Para cualquier alarma con exceso < 10% del rango disponible,
    la severidad debe ser "warning".
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.2)  # Leave room for exceedance
    alarm_high = max_range - (range_span * 0.2)
    
    # Calculate value with <10% exceedance (high alarm)
    available_range = max_range - alarm_high
    assume(available_range > 0.1)  # Need reasonable range
    
    exceedance = available_range * exceedance_factor
    value = alarm_high + exceedance + 0.001  # Slightly above threshold
    
    variable = Variable(
        variable_id="TEST-004",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-004",
        area="pre-treatment",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: Alarm must be triggered
    assert alarm_info.is_alarm is True, \
        f"Alarm should trigger"
    
    # Property: Exceedance must be < 10%
    assert alarm_info.exceedance_percent < 10.0, \
        f"Exceedance should be < 10%, got {alarm_info.exceedance_percent}%"
    
    # Property: Severity must be WARNING
    assert alarm_info.severity == AlarmSeverity.WARNING, \
        f"Severity should be WARNING for exceedance < 10%, got {alarm_info.severity}"


@settings(max_examples=200)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
    exceedance_factor=st.floats(min_value=0.11, max_value=0.9, allow_nan=False, allow_infinity=False)
)
def test_property_4_critical_severity_above_10_percent(min_range, max_range, exceedance_factor):
    """
    Property 4: Para cualquier alarma con exceso >= 10% del rango disponible,
    la severidad debe ser "critical".
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.2)  # Leave room for exceedance
    alarm_high = max_range - (range_span * 0.2)
    
    # Calculate value with >=10% exceedance (low alarm)
    available_range = alarm_low - min_range
    assume(available_range > 1.0)  # Need reasonable range
    
    exceedance = available_range * exceedance_factor
    value = alarm_low - exceedance
    
    variable = Variable(
        variable_id="TEST-005",
        name="Test Variable",
        area="e-coat",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-005",
        area="e-coat",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: Alarm must be triggered
    assert alarm_info.is_alarm is True, \
        f"Alarm should trigger"
    
    # Property: Exceedance must be >= 10%
    assert alarm_info.exceedance_percent >= 10.0, \
        f"Exceedance should be >= 10%, got {alarm_info.exceedance_percent}%"
    
    # Property: Severity must be CRITICAL
    assert alarm_info.severity == AlarmSeverity.CRITICAL, \
        f"Severity should be CRITICAL for exceedance >= 10%, got {alarm_info.severity}"


@settings(max_examples=100)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False)
)
def test_property_4_alarm_info_contains_required_fields(min_range, max_range):
    """
    Property 4: Toda alarma generada debe contener los campos requeridos:
    is_alarm, severity, threshold_type, threshold_value, exceedance_percent, message.
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.1)
    alarm_high = max_range - (range_span * 0.1)
    
    # Generate alarm condition (high alarm)
    value = alarm_high + 1.0
    
    variable = Variable(
        variable_id="TEST-006",
        name="Test Variable",
        area="production-control",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-006",
        area="production-control",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    alarm_info = simulator.check_alarm(data_point, variable)
    
    # Property: All required fields must be present
    assert hasattr(alarm_info, 'is_alarm'), "AlarmInfo must have 'is_alarm' field"
    assert hasattr(alarm_info, 'severity'), "AlarmInfo must have 'severity' field"
    assert hasattr(alarm_info, 'threshold_type'), "AlarmInfo must have 'threshold_type' field"
    assert hasattr(alarm_info, 'threshold_value'), "AlarmInfo must have 'threshold_value' field"
    assert hasattr(alarm_info, 'exceedance_percent'), "AlarmInfo must have 'exceedance_percent' field"
    assert hasattr(alarm_info, 'message'), "AlarmInfo must have 'message' field"
    
    # Property: When alarm is triggered, fields must have valid values
    if alarm_info.is_alarm:
        assert alarm_info.severity is not None, "Severity must not be None when alarm is triggered"
        assert alarm_info.threshold_type in ['low', 'high'], \
            f"Threshold type must be 'low' or 'high', got {alarm_info.threshold_type}"
        assert alarm_info.threshold_value is not None, "Threshold value must not be None"
        assert alarm_info.exceedance_percent is not None, "Exceedance percent must not be None"
        assert alarm_info.exceedance_percent >= 0.0, "Exceedance percent must be non-negative"
        assert alarm_info.message is not None, "Message must not be None"
        assert len(alarm_info.message) > 0, "Message must not be empty"


@settings(max_examples=100)
@given(
    min_range=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    max_range=st.floats(min_value=100.1, max_value=1000.0, allow_nan=False, allow_infinity=False)
)
def test_property_4_enrich_data_point_preserves_original_data(min_range, max_range):
    """
    Property 4: Al enriquecer un DataPoint con información de alarma,
    los datos originales del DataPoint deben preservarse.
    
    **Validates: Requirements 1.5, 4.2**
    """
    # Setup variable
    range_span = max_range - min_range
    alarm_low = min_range + (range_span * 0.1)
    alarm_high = max_range - (range_span * 0.1)
    
    # Generate value (may or may not trigger alarm)
    value = (alarm_low + alarm_high) / 2.0
    
    variable = Variable(
        variable_id="TEST-007",
        name="Test Variable",
        area="pre-treatment",
        unit="test",
        min_range=min_range,
        max_range=max_range,
        alarm_low=alarm_low,
        alarm_high=alarm_high,
        description="Test",
        source_file="test",
        active=True
    )
    
    data_point = DataPoint(
        variable_id="TEST-007",
        area="pre-treatment",
        timestamp="2024-01-15T10:30:00.000Z",
        value=value,
        unit="test",
        quality="good",
        metadata={
            "min_range": min_range,
            "max_range": max_range,
            "alarm_low": alarm_low,
            "alarm_high": alarm_high
        }
    )
    
    simulator = AlarmSimulator()
    enriched = simulator.enrich_data_point(data_point, variable)
    
    # Property: Original data must be preserved
    assert enriched["variable_id"] == data_point.variable_id, \
        "variable_id must be preserved"
    assert enriched["area"] == data_point.area, \
        "area must be preserved"
    assert enriched["timestamp"] == data_point.timestamp, \
        "timestamp must be preserved"
    assert enriched["value"] == data_point.value, \
        "value must be preserved"
    assert enriched["unit"] == data_point.unit, \
        "unit must be preserved"
    assert enriched["quality"] == data_point.quality, \
        "quality must be preserved"
    
    # Property: Alarm information must be added
    assert "alarm" in enriched, \
        "Enriched data must contain 'alarm' field"
    assert isinstance(enriched["alarm"], dict), \
        "Alarm field must be a dictionary"
    assert "is_alarm" in enriched["alarm"], \
        "Alarm field must contain 'is_alarm'"


@settings(max_examples=100)
@given(
    alarm_count=st.integers(min_value=1, max_value=100)
)
def test_property_4_statistics_track_alarm_counts(alarm_count):
    """
    Property 4: El simulador debe mantener estadísticas precisas del número
    de alarmas generadas (total, warnings, critical).
    
    **Validates: Requirements 1.5, 4.2**
    """
    simulator = AlarmSimulator()
    
    # Generate alarms
    variable = Variable(
        variable_id="TEST-008",
        name="Test Variable",
        area="e-coat",
        unit="test",
        min_range=0.0,
        max_range=100.0,
        alarm_low=10.0,
        alarm_high=90.0,
        description="Test",
        source_file="test",
        active=True
    )
    
    warning_count = 0
    critical_count = 0
    
    for i in range(alarm_count):
        # Alternate between warning and critical alarms
        if i % 2 == 0:
            # Warning: slightly above alarm_high (< 10% exceedance)
            # Available range = 100 - 90 = 10
            # For < 10% exceedance, need value < 91
            value = 90.5
            warning_count += 1
        else:
            # Critical: well above alarm_high (>= 10% exceedance)
            value = 95.0
            critical_count += 1
        
        data_point = DataPoint(
            variable_id="TEST-008",
            area="e-coat",
            timestamp="2024-01-15T10:30:00.000Z",
            value=value,
            unit="test",
            quality="good",
            metadata={
                "min_range": 0.0,
                "max_range": 100.0,
                "alarm_low": 10.0,
                "alarm_high": 90.0
            }
        )
        
        simulator.check_alarm(data_point, variable)
    
    # Property: Statistics must match actual counts
    stats = simulator.get_statistics()
    assert stats["total_alarms"] == alarm_count, \
        f"Total alarms should be {alarm_count}, got {stats['total_alarms']}"
    assert stats["warnings"] == warning_count, \
        f"Warnings should be {warning_count}, got {stats['warnings']}"
    assert stats["critical"] == critical_count, \
        f"Critical alarms should be {critical_count}, got {stats['critical']}"


def test_property_4_alarm_generation_with_real_variables():
    """
    Property 4: Las alarmas deben generarse correctamente para las variables
    reales cargadas desde los archivos CSV.
    
    **Validates: Requirements 1.5, 4.2**
    """
    from config_loader import ConfigLoader
    
    # Load real variables
    loader = ConfigLoader(base_path=Path(__file__).parent.parent.parent / "simulator")
    
    try:
        variables = loader.load_all()
    except FileNotFoundError:
        pytest.skip("CSV files not found - skipping test")
        return
    
    simulator = AlarmSimulator()
    
    # Test with first 10 variables
    test_vars = list(variables.values())[:10]
    
    for variable in test_vars:
        # Test low alarm
        low_alarm_value = variable.alarm_low - 1.0
        data_point_low = DataPoint(
            variable_id=variable.variable_id,
            area=variable.area,
            timestamp="2024-01-15T10:30:00.000Z",
            value=low_alarm_value,
            unit=variable.unit,
            quality="good",
            metadata={
                "min_range": variable.min_range,
                "max_range": variable.max_range,
                "alarm_low": variable.alarm_low,
                "alarm_high": variable.alarm_high
            }
        )
        
        alarm_info_low = simulator.check_alarm(data_point_low, variable)
        
        # Property: Low alarm must be triggered
        assert alarm_info_low.is_alarm is True, \
            f"Variable {variable.variable_id}: Low alarm should trigger"
        assert alarm_info_low.threshold_type == "low", \
            f"Variable {variable.variable_id}: Alarm type should be 'low'"
        
        # Test high alarm
        high_alarm_value = variable.alarm_high + 1.0
        data_point_high = DataPoint(
            variable_id=variable.variable_id,
            area=variable.area,
            timestamp="2024-01-15T10:30:00.000Z",
            value=high_alarm_value,
            unit=variable.unit,
            quality="good",
            metadata={
                "min_range": variable.min_range,
                "max_range": variable.max_range,
                "alarm_low": variable.alarm_low,
                "alarm_high": variable.alarm_high
            }
        )
        
        alarm_info_high = simulator.check_alarm(data_point_high, variable)
        
        # Property: High alarm must be triggered
        assert alarm_info_high.is_alarm is True, \
            f"Variable {variable.variable_id}: High alarm should trigger"
        assert alarm_info_high.threshold_type == "high", \
            f"Variable {variable.variable_id}: Alarm type should be 'high'"
        
        # Test normal value
        normal_value = (variable.alarm_low + variable.alarm_high) / 2.0
        data_point_normal = DataPoint(
            variable_id=variable.variable_id,
            area=variable.area,
            timestamp="2024-01-15T10:30:00.000Z",
            value=normal_value,
            unit=variable.unit,
            quality="good",
            metadata={
                "min_range": variable.min_range,
                "max_range": variable.max_range,
                "alarm_low": variable.alarm_low,
                "alarm_high": variable.alarm_high
            }
        )
        
        alarm_info_normal = simulator.check_alarm(data_point_normal, variable)
        
        # Property: No alarm should be triggered
        assert alarm_info_normal.is_alarm is False, \
            f"Variable {variable.variable_id}: No alarm should trigger for normal value"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
