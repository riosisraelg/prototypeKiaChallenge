"""
Alarm simulator module for KIA Paint Shop IoT Prototype.

This module detects when variable values exceed configured alarm thresholds
and calculates alarm severity based on the percentage of exceedance.

Features:
- Detect values exceeding alarm_low or alarm_high thresholds
- Calculate severity: warning (<10% exceedance) or critical (≥10% exceedance)
- Generate alarm metadata for inclusion in MQTT payload
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum

from config_loader import Variable
from data_generator import DataPoint

logger = logging.getLogger(__name__)


class AlarmSeverity(str, Enum):
    """Alarm severity levels."""
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlarmInfo:
    """Information about an alarm condition."""
    
    is_alarm: bool
    severity: Optional[AlarmSeverity]
    threshold_type: Optional[str]  # "low" or "high"
    threshold_value: Optional[float]
    exceedance_percent: Optional[float]
    message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "is_alarm": self.is_alarm,
        }
        
        if self.is_alarm:
            result.update({
                "severity": self.severity.value if self.severity else None,
                "threshold_type": self.threshold_type,
                "threshold_value": self.threshold_value,
                "exceedance_percent": round(self.exceedance_percent, 2) if self.exceedance_percent else None,
                "message": self.message
            })
        
        return result


class AlarmSimulator:
    """Detects alarm conditions and calculates severity."""
    
    def __init__(self):
        """Initialize the alarm simulator."""
        self.alarm_count = 0
        self.warning_count = 0
        self.critical_count = 0
    
    def check_alarm(self, data_point: DataPoint, variable: Variable) -> AlarmInfo:
        """
        Check if a data point triggers an alarm condition.
        
        Args:
            data_point: Data point to check
            variable: Variable configuration with alarm thresholds
            
        Returns:
            AlarmInfo with alarm status and details
        """
        value = data_point.value
        alarm_low = variable.alarm_low
        alarm_high = variable.alarm_high
        
        # Check if value exceeds thresholds
        if value < alarm_low:
            # Low alarm
            exceedance_percent = self._calculate_exceedance_percent(
                value, alarm_low, variable.min_range, is_low=True
            )
            severity = self._determine_severity(exceedance_percent)
            
            alarm_info = AlarmInfo(
                is_alarm=True,
                severity=severity,
                threshold_type="low",
                threshold_value=alarm_low,
                exceedance_percent=exceedance_percent,
                message=f"{variable.name} below low threshold: {value:.2f} < {alarm_low:.2f} {variable.unit}"
            )
            
            self._update_counters(severity)
            logger.warning(f"LOW ALARM: {alarm_info.message} (severity: {severity.value})")
            
            return alarm_info
            
        elif value > alarm_high:
            # High alarm
            exceedance_percent = self._calculate_exceedance_percent(
                value, alarm_high, variable.max_range, is_low=False
            )
            severity = self._determine_severity(exceedance_percent)
            
            alarm_info = AlarmInfo(
                is_alarm=True,
                severity=severity,
                threshold_type="high",
                threshold_value=alarm_high,
                exceedance_percent=exceedance_percent,
                message=f"{variable.name} above high threshold: {value:.2f} > {alarm_high:.2f} {variable.unit}"
            )
            
            self._update_counters(severity)
            logger.warning(f"HIGH ALARM: {alarm_info.message} (severity: {severity.value})")
            
            return alarm_info
        
        else:
            # No alarm
            return AlarmInfo(
                is_alarm=False,
                severity=None,
                threshold_type=None,
                threshold_value=None,
                exceedance_percent=None,
                message=None
            )
    
    def _calculate_exceedance_percent(
        self, 
        value: float, 
        threshold: float, 
        limit: float,
        is_low: bool
    ) -> float:
        """
        Calculate the percentage by which a value exceeds the threshold.
        
        For low alarms: percentage = (threshold - value) / (threshold - min_range) * 100
        For high alarms: percentage = (value - threshold) / (max_range - threshold) * 100
        
        Args:
            value: Actual value
            threshold: Alarm threshold (alarm_low or alarm_high)
            limit: Physical limit (min_range or max_range)
            is_low: True if this is a low alarm, False if high alarm
            
        Returns:
            Exceedance percentage (0-100+)
        """
        if is_low:
            # Low alarm: value < threshold
            # Calculate how far below threshold as percentage of available range
            available_range = threshold - limit
            if available_range <= 0:
                return 100.0  # Edge case: threshold equals limit
            
            exceedance = threshold - value
            exceedance_percent = (exceedance / available_range) * 100.0
        else:
            # High alarm: value > threshold
            # Calculate how far above threshold as percentage of available range
            available_range = limit - threshold
            if available_range <= 0:
                return 100.0  # Edge case: threshold equals limit
            
            exceedance = value - threshold
            exceedance_percent = (exceedance / available_range) * 100.0
        
        return exceedance_percent
    
    def _determine_severity(self, exceedance_percent: float) -> AlarmSeverity:
        """
        Determine alarm severity based on exceedance percentage.
        
        - warning: exceedance < 10%
        - critical: exceedance >= 10%
        
        Args:
            exceedance_percent: Percentage of exceedance
            
        Returns:
            AlarmSeverity enum value
        """
        if exceedance_percent >= 10.0:
            return AlarmSeverity.CRITICAL
        else:
            return AlarmSeverity.WARNING
    
    def _update_counters(self, severity: AlarmSeverity) -> None:
        """Update alarm counters."""
        self.alarm_count += 1
        
        if severity == AlarmSeverity.WARNING:
            self.warning_count += 1
        elif severity == AlarmSeverity.CRITICAL:
            self.critical_count += 1
    
    def enrich_data_point(self, data_point: DataPoint, variable: Variable) -> Dict[str, Any]:
        """
        Enrich a data point with alarm information.
        
        Args:
            data_point: Data point to enrich
            variable: Variable configuration
            
        Returns:
            Dictionary with data point and alarm information
        """
        # Check for alarm
        alarm_info = self.check_alarm(data_point, variable)
        
        # Convert data point to dict
        payload = data_point.to_dict()
        
        # Add alarm information
        payload["alarm"] = alarm_info.to_dict()
        
        return payload
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get alarm statistics.
        
        Returns:
            Dictionary with alarm counts
        """
        return {
            "total_alarms": self.alarm_count,
            "warnings": self.warning_count,
            "critical": self.critical_count
        }
    
    def reset_statistics(self) -> None:
        """Reset alarm counters."""
        self.alarm_count = 0
        self.warning_count = 0
        self.critical_count = 0
        logger.info("Alarm statistics reset")


def main():
    """Test the alarm simulator."""
    import sys
    from pathlib import Path
    
    # Add simulator to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from config_loader import ConfigLoader
    from data_generator import DataGenerator
    
    logging.basicConfig(level=logging.INFO)
    
    # Load variables
    loader = ConfigLoader()
    variables = loader.load_all()
    
    # Create generator and alarm simulator
    generator = DataGenerator(anomaly_probability=0.3)  # Higher probability for testing
    alarm_sim = AlarmSimulator()
    
    print(f"\n{'='*60}")
    print(f"Alarm Simulator Test")
    print(f"{'='*60}\n")
    
    # Test with first 5 variables
    test_vars = list(variables.values())[:5]
    
    print("Generating data with alarms...\n")
    
    for round_num in range(1, 4):
        print(f"Round {round_num}:")
        print("-" * 60)
        
        # Generate data points
        data_points = generator.generate_batch(test_vars, force_anomaly_count=2)
        
        for dp in data_points:
            var = variables[dp.variable_id]
            
            # Check for alarm
            alarm_info = alarm_sim.check_alarm(dp, var)
            
            print(f"{dp.variable_id}: {dp.value:.2f} {dp.unit}")
            print(f"  Range: [{var.min_range:.2f}, {var.max_range:.2f}]")
            print(f"  Alarm thresholds: [{var.alarm_low:.2f}, {var.alarm_high:.2f}]")
            
            if alarm_info.is_alarm:
                print(f"  🚨 ALARM: {alarm_info.severity.value.upper()}")
                print(f"     Type: {alarm_info.threshold_type}")
                print(f"     Exceedance: {alarm_info.exceedance_percent:.1f}%")
                print(f"     Message: {alarm_info.message}")
            else:
                print(f"  ✓ Normal")
            
            print()
        
        print()
    
    # Print statistics
    stats = alarm_sim.get_statistics()
    print(f"{'='*60}")
    print(f"Alarm Statistics:")
    print(f"  Total alarms: {stats['total_alarms']}")
    print(f"  Warnings: {stats['warnings']}")
    print(f"  Critical: {stats['critical']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
