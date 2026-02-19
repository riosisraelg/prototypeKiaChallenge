"""
Unit tests for alarm_simulator module.

Tests alarm detection, severity calculation, and alarm metadata generation.
"""

import pytest
from dataclasses import dataclass
from typing import Dict, Any

# Mock the imports since we're testing in isolation
@dataclass
class MockVariable:
    """Mock Variable class for testing."""
    variable_id: str
    name: str
    area: str
    unit: str
    min_range: float
    max_range: float
    alarm_low: float
    alarm_high: float


@dataclass
class MockDataPoint:
    """Mock DataPoint class for testing."""
    variable_id: str
    area: str
    timestamp: str
    value: float
    unit: str
    quality: str
    metadata: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "variable_id": self.variable_id,
            "area": self.area,
            "timestamp": self.timestamp,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality,
            "metadata": self.metadata
        }


# Import after mocking
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "simulator"))

from alarm_simulator import AlarmSimulator, AlarmSeverity, AlarmInfo


class TestAlarmInfo:
    """Tests for AlarmInfo dataclass."""
    
    def test_alarm_info_to_dict_no_alarm(self):
        """Test AlarmInfo.to_dict() when there's no alarm."""
        alarm_info = AlarmInfo(
            is_alarm=False,
            severity=None,
            threshold_type=None,
            threshold_value=None,
            exceedance_percent=None,
            message=None
        )
        
        result = alarm_info.to_dict()
        
        assert result == {"is_alarm": False}
    
    def test_alarm_info_to_dict_with_alarm(self):
        """Test AlarmInfo.to_dict() when there's an alarm."""
        alarm_info = AlarmInfo(
            is_alarm=True,
            severity=AlarmSeverity.WARNING,
            threshold_type="high",
            threshold_value=100.0,
            exceedance_percent=5.5,
            message="Test alarm"
        )
        
        result = alarm_info.to_dict()
        
        assert result["is_alarm"] is True
        assert result["severity"] == "warning"
        assert result["threshold_type"] == "high"
        assert result["threshold_value"] == 100.0
        assert result["exceedance_percent"] == 5.5
        assert result["message"] == "Test alarm"


class TestAlarmSimulator:
    """Tests for AlarmSimulator class."""
    
    @pytest.fixture
    def simulator(self):
        """Create a fresh AlarmSimulator instance."""
        return AlarmSimulator()
    
    @pytest.fixture
    def normal_variable(self):
        """Create a variable with normal ranges."""
        return MockVariable(
            variable_id="TEST-001",
            name="Test Variable",
            area="pre-treatment",
            unit="°C",
            min_range=60.0,
            max_range=80.0,
            alarm_low=65.0,
            alarm_high=75.0
        )
    
    def create_data_point(self, variable: MockVariable, value: float) -> MockDataPoint:
        """Helper to create a data point."""
        return MockDataPoint(
            variable_id=variable.variable_id,
            area=variable.area,
            timestamp="2024-01-15T10:30:00.000Z",
            value=value,
            unit=variable.unit,
            quality="good",
            metadata={
                "min_range": variable.min_range,
                "max_range": variable.max_range,
                "alarm_low": variable.alarm_low,
                "alarm_high": variable.alarm_high
            }
        )
    
    def test_no_alarm_within_thresholds(self, simulator, normal_variable):
        """Test that no alarm is generated when value is within thresholds."""
        data_point = self.create_data_point(normal_variable, 70.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is False
        assert alarm_info.severity is None
        assert alarm_info.threshold_type is None
        assert alarm_info.exceedance_percent is None
    
    def test_low_alarm_warning_severity(self, simulator, normal_variable):
        """Test low alarm with warning severity (<10% exceedance)."""
        # Value slightly below alarm_low
        # alarm_low = 65.0, min_range = 60.0
        # Available range = 65.0 - 60.0 = 5.0
        # For <10% exceedance, need value > 64.5 (0.5 / 5.0 = 10%)
        data_point = self.create_data_point(normal_variable, 64.6)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.severity == AlarmSeverity.WARNING
        assert alarm_info.threshold_type == "low"
        assert alarm_info.threshold_value == 65.0
        assert alarm_info.exceedance_percent < 10.0
        assert "below low threshold" in alarm_info.message
    
    def test_low_alarm_critical_severity(self, simulator, normal_variable):
        """Test low alarm with critical severity (≥10% exceedance)."""
        # Value well below alarm_low
        # alarm_low = 65.0, min_range = 60.0
        # Available range = 5.0
        # For ≥10% exceedance, need value ≤ 64.5
        data_point = self.create_data_point(normal_variable, 64.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.severity == AlarmSeverity.CRITICAL
        assert alarm_info.threshold_type == "low"
        assert alarm_info.exceedance_percent >= 10.0
    
    def test_high_alarm_warning_severity(self, simulator, normal_variable):
        """Test high alarm with warning severity (<10% exceedance)."""
        # Value slightly above alarm_high
        # alarm_high = 75.0, max_range = 80.0
        # Available range = 80.0 - 75.0 = 5.0
        # For <10% exceedance, need value < 75.5
        data_point = self.create_data_point(normal_variable, 75.4)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.severity == AlarmSeverity.WARNING
        assert alarm_info.threshold_type == "high"
        assert alarm_info.threshold_value == 75.0
        assert alarm_info.exceedance_percent < 10.0
        assert "above high threshold" in alarm_info.message
    
    def test_high_alarm_critical_severity(self, simulator, normal_variable):
        """Test high alarm with critical severity (≥10% exceedance)."""
        # Value well above alarm_high
        # alarm_high = 75.0, max_range = 80.0
        # Available range = 5.0
        # For ≥10% exceedance, need value ≥ 75.5
        data_point = self.create_data_point(normal_variable, 76.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.severity == AlarmSeverity.CRITICAL
        assert alarm_info.threshold_type == "high"
        assert alarm_info.exceedance_percent >= 10.0
    
    def test_exceedance_calculation_low_alarm(self, simulator, normal_variable):
        """Test exceedance percentage calculation for low alarm."""
        # alarm_low = 65.0, min_range = 60.0
        # Available range = 5.0
        # Value = 63.0, exceedance = 65.0 - 63.0 = 2.0
        # Percentage = (2.0 / 5.0) * 100 = 40%
        data_point = self.create_data_point(normal_variable, 63.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.exceedance_percent == pytest.approx(40.0, rel=0.01)
    
    def test_exceedance_calculation_high_alarm(self, simulator, normal_variable):
        """Test exceedance percentage calculation for high alarm."""
        # alarm_high = 75.0, max_range = 80.0
        # Available range = 5.0
        # Value = 77.0, exceedance = 77.0 - 75.0 = 2.0
        # Percentage = (2.0 / 5.0) * 100 = 40%
        data_point = self.create_data_point(normal_variable, 77.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        assert alarm_info.exceedance_percent == pytest.approx(40.0, rel=0.01)
    
    def test_alarm_at_exact_threshold(self, simulator, normal_variable):
        """Test that value exactly at threshold doesn't trigger alarm."""
        # Test at alarm_low
        data_point_low = self.create_data_point(normal_variable, 65.0)
        alarm_info_low = simulator.check_alarm(data_point_low, normal_variable)
        assert alarm_info_low.is_alarm is False
        
        # Test at alarm_high
        data_point_high = self.create_data_point(normal_variable, 75.0)
        alarm_info_high = simulator.check_alarm(data_point_high, normal_variable)
        assert alarm_info_high.is_alarm is False
    
    def test_alarm_counters(self, simulator, normal_variable):
        """Test that alarm counters are updated correctly."""
        # Generate warning alarm
        data_point_warning = self.create_data_point(normal_variable, 64.6)
        simulator.check_alarm(data_point_warning, normal_variable)
        
        # Generate critical alarm
        data_point_critical = self.create_data_point(normal_variable, 64.0)
        simulator.check_alarm(data_point_critical, normal_variable)
        
        # Generate another critical alarm
        data_point_critical2 = self.create_data_point(normal_variable, 76.0)
        simulator.check_alarm(data_point_critical2, normal_variable)
        
        stats = simulator.get_statistics()
        
        assert stats["total_alarms"] == 3
        assert stats["warnings"] == 1
        assert stats["critical"] == 2
    
    def test_reset_statistics(self, simulator, normal_variable):
        """Test that statistics can be reset."""
        # Generate some alarms
        data_point = self.create_data_point(normal_variable, 64.0)
        simulator.check_alarm(data_point, normal_variable)
        
        # Reset
        simulator.reset_statistics()
        
        stats = simulator.get_statistics()
        assert stats["total_alarms"] == 0
        assert stats["warnings"] == 0
        assert stats["critical"] == 0
    
    def test_enrich_data_point_no_alarm(self, simulator, normal_variable):
        """Test enriching data point when there's no alarm."""
        data_point = self.create_data_point(normal_variable, 70.0)
        
        enriched = simulator.enrich_data_point(data_point, normal_variable)
        
        assert enriched["variable_id"] == "TEST-001"
        assert enriched["value"] == 70.0
        assert "alarm" in enriched
        assert enriched["alarm"]["is_alarm"] is False
    
    def test_enrich_data_point_with_alarm(self, simulator, normal_variable):
        """Test enriching data point when there's an alarm."""
        data_point = self.create_data_point(normal_variable, 64.0)
        
        enriched = simulator.enrich_data_point(data_point, normal_variable)
        
        assert enriched["variable_id"] == "TEST-001"
        assert enriched["value"] == 64.0
        assert "alarm" in enriched
        assert enriched["alarm"]["is_alarm"] is True
        assert enriched["alarm"]["severity"] == "critical"
        assert enriched["alarm"]["threshold_type"] == "low"
    
    def test_edge_case_threshold_equals_limit(self, simulator):
        """Test edge case where threshold equals physical limit."""
        # Create variable where alarm_low equals min_range
        variable = MockVariable(
            variable_id="EDGE-001",
            name="Edge Case Variable",
            area="pre-treatment",
            unit="bar",
            min_range=50.0,
            max_range=100.0,
            alarm_low=50.0,  # Same as min_range
            alarm_high=100.0  # Same as max_range
        )
        
        # Value below alarm_low (which equals min_range)
        data_point = self.create_data_point(variable, 49.0)
        
        alarm_info = simulator.check_alarm(data_point, variable)
        
        # Should still generate alarm with 100% exceedance
        assert alarm_info.is_alarm is True
        assert alarm_info.exceedance_percent == 100.0
        assert alarm_info.severity == AlarmSeverity.CRITICAL
    
    def test_severity_boundary_exactly_10_percent(self, simulator, normal_variable):
        """Test severity determination at exactly 10% exceedance."""
        # alarm_low = 65.0, min_range = 60.0
        # Available range = 5.0
        # For exactly 10% exceedance: value = 65.0 - 0.5 = 64.5
        data_point = self.create_data_point(normal_variable, 64.5)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        assert alarm_info.is_alarm is True
        # At exactly 10%, should be CRITICAL (≥10%)
        assert alarm_info.severity == AlarmSeverity.CRITICAL
        assert alarm_info.exceedance_percent == pytest.approx(10.0, rel=0.01)
    
    def test_message_format(self, simulator, normal_variable):
        """Test that alarm messages contain required information."""
        data_point = self.create_data_point(normal_variable, 64.0)
        
        alarm_info = simulator.check_alarm(data_point, normal_variable)
        
        message = alarm_info.message
        assert normal_variable.name in message
        assert "64.00" in message
        assert "65.00" in message
        assert normal_variable.unit in message
        assert "below low threshold" in message


class TestAlarmSimulatorIntegration:
    """Integration tests for alarm simulator with realistic scenarios."""
    
    def test_multiple_variables_different_alarms(self):
        """Test alarm detection across multiple variables."""
        simulator = AlarmSimulator()
        
        # Variable 1: Normal
        var1 = MockVariable("VAR-001", "Var 1", "pre-treatment", "°C", 60, 80, 65, 75)
        dp1 = MockDataPoint("VAR-001", "pre-treatment", "2024-01-15T10:30:00Z", 
                           70.0, "°C", "good", {"min_range": 60, "max_range": 80, 
                           "alarm_low": 65, "alarm_high": 75})
        
        # Variable 2: Low alarm (warning)
        # alarm_low=55, min_range=50, available_range=5
        # For <10% exceedance, need value > 54.5 (0.5/5 = 10%)
        # Use 54.6 for warning (0.4/5 = 8%)
        var2 = MockVariable("VAR-002", "Var 2", "e-coat", "bar", 50, 100, 55, 95)
        dp2 = MockDataPoint("VAR-002", "e-coat", "2024-01-15T10:30:00Z",
                           54.6, "bar", "good", {"min_range": 50, "max_range": 100,
                           "alarm_low": 55, "alarm_high": 95})
        
        # Variable 3: High alarm (critical)
        var3 = MockVariable("VAR-003", "Var 3", "production-control", "V", 200, 300, 210, 290)
        dp3 = MockDataPoint("VAR-003", "production-control", "2024-01-15T10:30:00Z",
                           295.0, "V", "good", {"min_range": 200, "max_range": 300,
                           "alarm_low": 210, "alarm_high": 290})
        
        # Check alarms
        alarm1 = simulator.check_alarm(dp1, var1)
        alarm2 = simulator.check_alarm(dp2, var2)
        alarm3 = simulator.check_alarm(dp3, var3)
        
        # Verify results
        assert alarm1.is_alarm is False
        assert alarm2.is_alarm is True
        assert alarm2.severity == AlarmSeverity.WARNING
        assert alarm3.is_alarm is True
        assert alarm3.severity == AlarmSeverity.CRITICAL
        
        # Verify statistics
        stats = simulator.get_statistics()
        assert stats["total_alarms"] == 2
        assert stats["warnings"] == 1
        assert stats["critical"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
