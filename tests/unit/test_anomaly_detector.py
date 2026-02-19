"""
Unit tests for anomaly_detector module.

Tests the anomaly detection logic for the Lambda process function,
including threshold comparison, severity calculation, and message formatting.
"""

import pytest
import sys
from pathlib import Path

# Add lambdas/process to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "lambdas" / "process"))

from anomaly_detector import AnomalyDetector, AlarmSeverity, AlarmResult


class TestAnomalyDetector:
    """Test suite for AnomalyDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = AnomalyDetector()
    
    def test_no_alarm_within_range(self):
        """Test that no alarm is generated when value is within thresholds."""
        result = self.detector.detect(
            value=65.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        
        assert result.is_alarm is False
        assert result.severity is None
        assert result.threshold_type is None
        assert result.exceedance_percent is None
        assert result.message is None
    
    def test_low_alarm_warning_severity(self):
        """Test low alarm with warning severity (<10% exceedance)."""
        # Value: 58, threshold: 60, min_range: 50
        # Exceedance: 60 - 58 = 2
        # Available range: 60 - 50 = 10
        # Exceedance %: (2 / 10) * 100 = 20% -> CRITICAL
        # Let's test with smaller exceedance
        result = self.detector.detect(
            value=59.5,  # 0.5 below threshold
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="PT-TEMP-001",
            unit="°C"
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.WARNING
        assert result.threshold_type == "low"
        assert result.threshold_value == 60.0
        assert result.exceedance_percent == pytest.approx(5.0, rel=0.1)  # (0.5 / 10) * 100 = 5%
        assert "below low threshold" in result.message
        assert "PT-TEMP-001" in result.message
    
    def test_low_alarm_critical_severity(self):
        """Test low alarm with critical severity (≥10% exceedance)."""
        # Value: 58, threshold: 60, min_range: 50
        # Exceedance: 60 - 58 = 2
        # Available range: 60 - 50 = 10
        # Exceedance %: (2 / 10) * 100 = 20% -> CRITICAL
        result = self.detector.detect(
            value=58.0,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="PT-TEMP-001",
            unit="°C"
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.CRITICAL
        assert result.threshold_type == "low"
        assert result.threshold_value == 60.0
        assert result.exceedance_percent == pytest.approx(20.0, rel=0.1)
        assert "below low threshold" in result.message
    
    def test_high_alarm_warning_severity(self):
        """Test high alarm with warning severity (<10% exceedance)."""
        # Value: 70.5, threshold: 70, max_range: 80
        # Exceedance: 70.5 - 70 = 0.5
        # Available range: 80 - 70 = 10
        # Exceedance %: (0.5 / 10) * 100 = 5% -> WARNING
        result = self.detector.detect(
            value=70.5,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="PT-TEMP-001",
            unit="°C"
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.WARNING
        assert result.threshold_type == "high"
        assert result.threshold_value == 70.0
        assert result.exceedance_percent == pytest.approx(5.0, rel=0.1)
        assert "above high threshold" in result.message
    
    def test_high_alarm_critical_severity(self):
        """Test high alarm with critical severity (≥10% exceedance)."""
        # Value: 72, threshold: 70, max_range: 80
        # Exceedance: 72 - 70 = 2
        # Available range: 80 - 70 = 10
        # Exceedance %: (2 / 10) * 100 = 20% -> CRITICAL
        result = self.detector.detect(
            value=72.0,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="PT-TEMP-001",
            unit="°C"
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.CRITICAL
        assert result.threshold_type == "high"
        assert result.threshold_value == 70.0
        assert result.exceedance_percent == pytest.approx(20.0, rel=0.1)
        assert "above high threshold" in result.message
    
    def test_exceedance_at_exactly_10_percent(self):
        """Test that exactly 10% exceedance is classified as CRITICAL."""
        # Value: 71, threshold: 70, max_range: 80
        # Exceedance: 71 - 70 = 1
        # Available range: 80 - 70 = 10
        # Exceedance %: (1 / 10) * 100 = 10% -> CRITICAL
        result = self.detector.detect(
            value=71.0,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.CRITICAL
        assert result.exceedance_percent == pytest.approx(10.0, rel=0.1)
    
    def test_exceedance_without_limits(self):
        """Test exceedance calculation when min/max ranges are not provided."""
        # Should use threshold-based calculation
        result = self.detector.detect(
            value=72.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        
        assert result.is_alarm is True
        assert result.severity is not None
        assert result.exceedance_percent is not None
        assert result.exceedance_percent > 0
    
    def test_alarm_result_to_dict_with_alarm(self):
        """Test AlarmResult.to_dict() when alarm is present."""
        result = self.detector.detect(
            value=72.0,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="TEST-VAR",
            unit="units"
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["is_alarm"] is True
        assert result_dict["severity"] == "critical"
        assert result_dict["threshold_type"] == "high"
        assert result_dict["threshold_value"] == 70.0
        assert result_dict["exceedance_percent"] == pytest.approx(20.0, rel=0.1)
        assert result_dict["message"] is not None
        assert result_dict["value"] == 72.0
    
    def test_alarm_result_to_dict_no_alarm(self):
        """Test AlarmResult.to_dict() when no alarm is present."""
        result = self.detector.detect(
            value=65.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        
        result_dict = result.to_dict()
        
        assert result_dict == {"is_alarm": False}
    
    def test_message_formatting_with_all_params(self):
        """Test message formatting with all optional parameters."""
        result = self.detector.detect(
            value=72.5,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0,
            variable_name="PT-TEMP-001",
            unit="°C"
        )
        
        assert "PT-TEMP-001" in result.message
        assert "72.5" in result.message or "72.50" in result.message
        assert "70.0" in result.message or "70.00" in result.message
        assert "°C" in result.message
        assert "above high threshold" in result.message
    
    def test_message_formatting_without_optional_params(self):
        """Test message formatting without optional parameters."""
        result = self.detector.detect(
            value=72.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        
        assert result.message is not None
        assert "Variable" in result.message  # Default name
        assert "72" in result.message
        assert "70" in result.message
    
    def test_edge_case_threshold_equals_limit(self):
        """Test edge case where threshold equals physical limit."""
        # This should handle gracefully and return 100% exceedance
        result = self.detector.detect(
            value=72.0,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=70.0  # max_range equals alarm_high
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.CRITICAL
        assert result.exceedance_percent == 100.0
    
    def test_value_at_threshold_boundary(self):
        """Test values exactly at threshold boundaries."""
        # Value exactly at alarm_low should not trigger alarm
        result_low = self.detector.detect(
            value=60.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        assert result_low.is_alarm is False
        
        # Value exactly at alarm_high should not trigger alarm
        result_high = self.detector.detect(
            value=70.0,
            alarm_low=60.0,
            alarm_high=70.0
        )
        assert result_high.is_alarm is False
    
    def test_very_small_exceedance(self):
        """Test very small exceedance values."""
        result = self.detector.detect(
            value=70.01,
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.WARNING
        assert result.exceedance_percent < 1.0
    
    def test_very_large_exceedance(self):
        """Test very large exceedance values (beyond physical limits)."""
        result = self.detector.detect(
            value=85.0,  # Beyond max_range
            alarm_low=60.0,
            alarm_high=70.0,
            min_range=50.0,
            max_range=80.0
        )
        
        assert result.is_alarm is True
        assert result.severity == AlarmSeverity.CRITICAL
        assert result.exceedance_percent > 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
