"""
Property-based tests for statistical calculations.

Feature: kia-paint-shop-iot-prototype
Property 10: Correctitud de cálculos estadísticos

Tests that statistical calculations (average, min, max, standard deviation)
are mathematically correct for any set of valid sensor values.

Validates: Requirements 4.1, 5.5
"""

import sys
from pathlib import Path

# Add lambdas to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lambdas" / "statistics"))

from hypothesis import given, strategies as st, settings, assume
import pytest
import numpy as np
from statistics_calculator import StatisticsCalculator, StatisticsResult


# Feature: kia-paint-shop-iot-prototype, Property 10: Correctitud de cálculos estadísticos
@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_average_calculation_is_correct(values):
    """
    Property 10: Para cualquier conjunto de valores numéricos válidos,
    el promedio calculado debe ser matemáticamente correcto (±0.01 precisión).
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True, \
        f"Result should be valid for {len(values)} data points"
    
    # Property: Average must be mathematically correct
    expected_avg = np.mean(values)
    assert result.avg is not None, "Average must not be None"
    assert abs(result.avg - expected_avg) <= 0.01, \
        f"Average {result.avg} differs from expected {expected_avg} by more than 0.01"


@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_min_calculation_is_correct(values):
    """
    Property 10: Para cualquier conjunto de valores numéricos válidos,
    el mínimo calculado debe ser matemáticamente correcto.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True, \
        f"Result should be valid for {len(values)} data points"
    
    # Property: Min must be mathematically correct
    expected_min = np.min(values)
    assert result.min is not None, "Min must not be None"
    assert abs(result.min - expected_min) <= 0.01, \
        f"Min {result.min} differs from expected {expected_min} by more than 0.01"
    
    # Property: Min must be <= all values
    for value in values:
        assert result.min <= value, \
            f"Min {result.min} should be <= all values, but {value} is smaller"


@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_max_calculation_is_correct(values):
    """
    Property 10: Para cualquier conjunto de valores numéricos válidos,
    el máximo calculado debe ser matemáticamente correcto.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True, \
        f"Result should be valid for {len(values)} data points"
    
    # Property: Max must be mathematically correct
    expected_max = np.max(values)
    assert result.max is not None, "Max must not be None"
    assert abs(result.max - expected_max) <= 0.01, \
        f"Max {result.max} differs from expected {expected_max} by more than 0.01"
    
    # Property: Max must be >= all values
    for value in values:
        assert result.max >= value, \
            f"Max {result.max} should be >= all values, but {value} is larger"


@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_stddev_calculation_is_correct(values):
    """
    Property 10: Para cualquier conjunto de valores numéricos válidos,
    la desviación estándar calculada debe ser matemáticamente correcta (±0.01 precisión).
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True, \
        f"Result should be valid for {len(values)} data points"
    
    # Property: Stddev must be mathematically correct (sample stddev with ddof=1)
    expected_stddev = np.std(values, ddof=1)
    assert result.stddev is not None, "Stddev must not be None"
    assert abs(result.stddev - expected_stddev) <= 0.01, \
        f"Stddev {result.stddev} differs from expected {expected_stddev} by more than 0.01"
    
    # Property: Stddev must be non-negative
    assert result.stddev >= 0.0, \
        f"Stddev must be non-negative, got {result.stddev}"


@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_count_is_correct(values):
    """
    Property 10: Para cualquier conjunto de valores, el conteo debe ser exacto.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Count must match input length
    assert result.count == len(values), \
        f"Count {result.count} should match input length {len(values)}"


@settings(max_examples=200)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=100
    )
)
def test_property_10_min_max_relationship(values):
    """
    Property 10: Para cualquier conjunto de valores, min <= avg <= max.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True
    
    # Property: min <= avg <= max
    assert result.min <= result.avg, \
        f"Min {result.min} should be <= avg {result.avg}"
    assert result.avg <= result.max, \
        f"Avg {result.avg} should be <= max {result.max}"


@settings(max_examples=100)
@given(
    constant_value=st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
    count=st.integers(min_value=3, max_value=50)
)
def test_property_10_constant_values_have_zero_stddev(constant_value, count):
    """
    Property 10: Para cualquier conjunto de valores constantes,
    la desviación estándar debe ser 0 (o muy cercana a 0).
    
    **Validates: Requirements 4.1, 5.5**
    """
    values = [constant_value] * count
    
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be valid
    assert result.is_valid is True
    
    # Property: All statistics should equal the constant value
    assert abs(result.avg - constant_value) <= 0.01, \
        f"Avg should be {constant_value}, got {result.avg}"
    assert abs(result.min - constant_value) <= 0.01, \
        f"Min should be {constant_value}, got {result.min}"
    assert abs(result.max - constant_value) <= 0.01, \
        f"Max should be {constant_value}, got {result.max}"
    
    # Property: Stddev should be 0 (or very close)
    assert result.stddev <= 0.01, \
        f"Stddev should be ~0 for constant values, got {result.stddev}"


@settings(max_examples=100)
@given(
    insufficient_count=st.integers(min_value=0, max_value=2)
)
def test_property_10_insufficient_data_points_returns_invalid(insufficient_count):
    """
    Property 10: Para cualquier conjunto con menos de 3 valores,
    el resultado debe ser inválido con mensaje de error apropiado.
    
    **Validates: Requirements 4.1, 5.5**
    """
    values = [1.0] * insufficient_count
    
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Property: Result must be invalid
    assert result.is_valid is False, \
        f"Result should be invalid for {insufficient_count} data points"
    
    # Property: Error message must be present
    assert result.error_message is not None, \
        "Error message must be present for invalid result"
    
    # Property: Statistics should be None
    assert result.avg is None, "Avg should be None for invalid result"
    assert result.min is None, "Min should be None for invalid result"
    assert result.max is None, "Max should be None for invalid result"
    assert result.stddev is None, "Stddev should be None for invalid result"


def test_property_10_empty_list_returns_invalid():
    """
    Property 10: Para una lista vacía, el resultado debe ser inválido.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate([])
    
    # Property: Result must be invalid
    assert result.is_valid is False, \
        "Result should be invalid for empty list"
    
    # Property: Count should be 0
    assert result.count == 0, \
        f"Count should be 0 for empty list, got {result.count}"
    
    # Property: Error message must mention no data
    assert "no data" in result.error_message.lower(), \
        f"Error message should mention 'no data', got: {result.error_message}"


@settings(max_examples=100)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=50
    )
)
def test_property_10_calculate_from_data_points_matches_calculate(values):
    """
    Property 10: calculate_from_data_points debe producir los mismos resultados
    que calculate cuando se extraen valores correctamente.
    
    **Validates: Requirements 4.1, 5.5**
    """
    # Create data points (simulating DynamoDB items)
    data_points = [{'value': v, 'timestamp': '2024-01-15T10:30:00Z'} for v in values]
    
    calculator = StatisticsCalculator()
    
    # Calculate using both methods
    result_direct = calculator.calculate(values)
    result_from_points = calculator.calculate_from_data_points(data_points)
    
    # Property: Both results must be valid
    assert result_direct.is_valid is True
    assert result_from_points.is_valid is True
    
    # Property: Results must match
    assert abs(result_direct.avg - result_from_points.avg) <= 0.01, \
        f"Avg mismatch: {result_direct.avg} vs {result_from_points.avg}"
    assert abs(result_direct.min - result_from_points.min) <= 0.01, \
        f"Min mismatch: {result_direct.min} vs {result_from_points.min}"
    assert abs(result_direct.max - result_from_points.max) <= 0.01, \
        f"Max mismatch: {result_direct.max} vs {result_from_points.max}"
    assert abs(result_direct.stddev - result_from_points.stddev) <= 0.01, \
        f"Stddev mismatch: {result_direct.stddev} vs {result_from_points.stddev}"
    assert result_direct.count == result_from_points.count, \
        f"Count mismatch: {result_direct.count} vs {result_from_points.count}"


@settings(max_examples=100)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=50
    )
)
def test_property_10_to_dict_contains_all_fields(values):
    """
    Property 10: El método to_dict debe incluir todos los campos requeridos
    cuando el resultado es válido.
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Convert to dict
    result_dict = result.to_dict()
    
    # Property: Dict must contain required fields
    assert 'count' in result_dict, "Dict must contain 'count'"
    assert 'is_valid' in result_dict, "Dict must contain 'is_valid'"
    
    if result.is_valid:
        assert 'avg' in result_dict, "Dict must contain 'avg' for valid result"
        assert 'min' in result_dict, "Dict must contain 'min' for valid result"
        assert 'max' in result_dict, "Dict must contain 'max' for valid result"
        assert 'stddev' in result_dict, "Dict must contain 'stddev' for valid result"
        
        # Property: Values must match
        assert result_dict['count'] == result.count
        assert abs(result_dict['avg'] - result.avg) <= 0.01
        assert abs(result_dict['min'] - result.min) <= 0.01
        assert abs(result_dict['max'] - result.max) <= 0.01
        assert abs(result_dict['stddev'] - result.stddev) <= 0.01
    else:
        assert 'error_message' in result_dict, \
            "Dict must contain 'error_message' for invalid result"


@settings(max_examples=100)
@given(
    values=st.lists(
        st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
        min_size=10,
        max_size=100
    )
)
def test_property_10_statistics_are_stable_across_permutations(values):
    """
    Property 10: Las estadísticas deben ser las mismas independientemente
    del orden de los valores (excepto para casos de precisión numérica).
    
    **Validates: Requirements 4.1, 5.5**
    """
    import random
    
    calculator = StatisticsCalculator()
    
    # Calculate with original order
    result1 = calculator.calculate(values)
    
    # Shuffle and calculate again
    shuffled = values.copy()
    random.shuffle(shuffled)
    result2 = calculator.calculate(shuffled)
    
    # Property: Results must be the same (within numerical precision)
    assert result1.is_valid == result2.is_valid
    assert result1.count == result2.count
    
    if result1.is_valid:
        assert abs(result1.avg - result2.avg) <= 0.01, \
            f"Avg should be stable: {result1.avg} vs {result2.avg}"
        assert abs(result1.min - result2.min) <= 0.01, \
            f"Min should be stable: {result1.min} vs {result2.min}"
        assert abs(result1.max - result2.max) <= 0.01, \
            f"Max should be stable: {result1.max} vs {result2.max}"
        assert abs(result1.stddev - result2.stddev) <= 0.01, \
            f"Stddev should be stable: {result1.stddev} vs {result2.stddev}"


@settings(max_examples=100)
@given(
    base_value=st.floats(min_value=10.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    count=st.integers(min_value=3, max_value=50)
)
def test_property_10_adding_extreme_value_affects_statistics(base_value, count):
    """
    Property 10: Agregar un valor extremo debe afectar las estadísticas
    de manera predecible (aumentar max o disminuir min).
    
    **Validates: Requirements 4.1, 5.5**
    """
    # Create base values around base_value
    values = [base_value] * count
    
    calculator = StatisticsCalculator()
    result_base = calculator.calculate(values)
    
    # Add extreme high value
    values_with_high = values + [base_value * 2.0]
    result_high = calculator.calculate(values_with_high)
    
    # Property: Max should increase
    assert result_high.max > result_base.max, \
        f"Max should increase when adding high value"
    
    # Property: Avg should increase
    assert result_high.avg > result_base.avg, \
        f"Avg should increase when adding high value"
    
    # Property: Stddev should increase (more spread)
    assert result_high.stddev > result_base.stddev, \
        f"Stddev should increase when adding extreme value"
    
    # Add extreme low value
    values_with_low = values + [base_value * 0.5]
    result_low = calculator.calculate(values_with_low)
    
    # Property: Min should decrease
    assert result_low.min < result_base.min, \
        f"Min should decrease when adding low value"
    
    # Property: Avg should decrease
    assert result_low.avg < result_base.avg, \
        f"Avg should decrease when adding low value"


@settings(max_examples=50)
@given(
    values=st.lists(
        st.floats(min_value=-1000.0, max_value=1000.0, allow_nan=False, allow_infinity=False),
        min_size=3,
        max_size=20
    )
)
def test_property_10_statistics_match_numpy_exactly(values):
    """
    Property 10: Los cálculos deben coincidir exactamente con numpy
    (la implementación de referencia).
    
    **Validates: Requirements 4.1, 5.5**
    """
    calculator = StatisticsCalculator()
    result = calculator.calculate(values)
    
    # Calculate using numpy directly
    data = np.array(values, dtype=np.float64)
    expected_avg = float(np.mean(data))
    expected_min = float(np.min(data))
    expected_max = float(np.max(data))
    expected_stddev = float(np.std(data, ddof=1))
    
    # Property: Results must match numpy exactly (within floating point precision)
    assert abs(result.avg - expected_avg) < 1e-10, \
        f"Avg must match numpy: {result.avg} vs {expected_avg}"
    assert abs(result.min - expected_min) < 1e-10, \
        f"Min must match numpy: {result.min} vs {expected_min}"
    assert abs(result.max - expected_max) < 1e-10, \
        f"Max must match numpy: {result.max} vs {expected_max}"
    assert abs(result.stddev - expected_stddev) < 1e-10, \
        f"Stddev must match numpy: {result.stddev} vs {expected_stddev}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
