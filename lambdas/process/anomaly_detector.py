"""
Anomaly detector module for KIA Paint Shop IoT Prototype Lambda process function.

This module detects when sensor values exceed configured alarm thresholds
and calculates alarm severity based on the percentage of exceedance.

Features:
- Compare current value with alarm thresholds (alarm_low, alarm_high)
- Calculate percentage of excess to determine severity
- Return alarm with metadata (severity, message, threshold)
- Severity levels: warning (<10% excess) or critical (≥10% excess)

Validates Requirements: 4.2, 4.4
"""

import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class AlarmSeverity(str, Enum):
    """Alarm severity levels."""
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AlarmResult:
    """Result of anomaly detection."""
    
    is_alarm: bool
    severity: Optional[AlarmSeverity]
    threshold_type: Optional[str]  # "low" or "high"
    threshold_value: Optional[float]
    exceedance_percent: Optional[float]
    message: Optional[str]
    value: Optional[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        if not self.is_alarm:
            return {"is_alarm": False}
        
        return {
            "is_alarm": True,
            "severity": self.severity.value if self.severity else None,
            "threshold_type": self.threshold_type,
            "threshold_value": self.threshold_value,
            "exceedance_percent": round(self.exceedance_percent, 2) if self.exceedance_percent is not None else None,
            "message": self.message,
            "value": self.value
        }


class AnomalyDetector:
    """Detects anomalies by comparing values against alarm thresholds."""
    
    def detect(
        self,
        value: float,
        alarm_low: float,
        alarm_high: float,
        min_range: Optional[float] = None,
        max_range: Optional[float] = None,
        variable_name: Optional[str] = None,
        unit: Optional[str] = None
    ) -> AlarmResult:
        """
        Detect if a value exceeds alarm thresholds and calculate severity.
        
        Args:
            value: Current sensor value
            alarm_low: Low alarm threshold
            alarm_high: High alarm threshold
            min_range: Minimum physical range (optional, for better exceedance calculation)
            max_range: Maximum physical range (optional, for better exceedance calculation)
            variable_name: Variable name for message (optional)
            unit: Unit of measurement for message (optional)
            
        Returns:
            AlarmResult with alarm status and metadata
        """
        # Check if value exceeds low threshold
        if value < alarm_low:
            exceedance_percent = self._calculate_exceedance_percent(
                value=value,
                threshold=alarm_low,
                limit=min_range,
                is_low=True
            )
            severity = self._determine_severity(exceedance_percent)
            
            message = self._format_message(
                variable_name=variable_name,
                value=value,
                threshold=alarm_low,
                unit=unit,
                threshold_type="low"
            )
            
            logger.warning(
                f"Low alarm detected: {message} "
                f"(exceedance: {exceedance_percent:.1f}%, severity: {severity.value})"
            )
            
            return AlarmResult(
                is_alarm=True,
                severity=severity,
                threshold_type="low",
                threshold_value=alarm_low,
                exceedance_percent=exceedance_percent,
                message=message,
                value=value
            )
        
        # Check if value exceeds high threshold
        elif value > alarm_high:
            exceedance_percent = self._calculate_exceedance_percent(
                value=value,
                threshold=alarm_high,
                limit=max_range,
                is_low=False
            )
            severity = self._determine_severity(exceedance_percent)
            
            message = self._format_message(
                variable_name=variable_name,
                value=value,
                threshold=alarm_high,
                unit=unit,
                threshold_type="high"
            )
            
            logger.warning(
                f"High alarm detected: {message} "
                f"(exceedance: {exceedance_percent:.1f}%, severity: {severity.value})"
            )
            
            return AlarmResult(
                is_alarm=True,
                severity=severity,
                threshold_type="high",
                threshold_value=alarm_high,
                exceedance_percent=exceedance_percent,
                message=message,
                value=value
            )
        
        # No alarm condition
        return AlarmResult(
            is_alarm=False,
            severity=None,
            threshold_type=None,
            threshold_value=None,
            exceedance_percent=None,
            message=None,
            value=value
        )
    
    def _calculate_exceedance_percent(
        self,
        value: float,
        threshold: float,
        limit: Optional[float],
        is_low: bool
    ) -> float:
        """
        Calculate the percentage by which a value exceeds the threshold.
        
        For low alarms: percentage = (threshold - value) / (threshold - min_range) * 100
        For high alarms: percentage = (value - threshold) / (max_range - threshold) * 100
        
        If limit is not provided, calculate based on threshold distance.
        
        Args:
            value: Actual value
            threshold: Alarm threshold (alarm_low or alarm_high)
            limit: Physical limit (min_range or max_range), optional
            is_low: True if this is a low alarm, False if high alarm
            
        Returns:
            Exceedance percentage (0-100+)
        """
        if is_low:
            # Low alarm: value < threshold
            exceedance = threshold - value
            
            if limit is not None:
                available_range = threshold - limit
                if available_range <= 0:
                    # Edge case: threshold equals or below limit
                    return 100.0
                exceedance_percent = (exceedance / available_range) * 100.0
            else:
                # No limit provided, use threshold as reference
                # Assume 10% below threshold is 100% exceedance
                reference_range = threshold * 0.1
                if reference_range <= 0:
                    return 100.0
                exceedance_percent = (exceedance / reference_range) * 100.0
        else:
            # High alarm: value > threshold
            exceedance = value - threshold
            
            if limit is not None:
                available_range = limit - threshold
                if available_range <= 0:
                    # Edge case: threshold equals or above limit
                    return 100.0
                exceedance_percent = (exceedance / available_range) * 100.0
            else:
                # No limit provided, use threshold as reference
                # Assume 10% above threshold is 100% exceedance
                reference_range = threshold * 0.1
                if reference_range <= 0:
                    return 100.0
                exceedance_percent = (exceedance / reference_range) * 100.0
        
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
    
    def _format_message(
        self,
        variable_name: Optional[str],
        value: float,
        threshold: float,
        unit: Optional[str],
        threshold_type: str
    ) -> str:
        """
        Format alarm message.
        
        Args:
            variable_name: Variable name
            value: Current value
            threshold: Threshold value
            unit: Unit of measurement
            threshold_type: "low" or "high"
            
        Returns:
            Formatted message string
        """
        var_display = variable_name if variable_name else "Variable"
        unit_display = f" {unit}" if unit else ""
        
        if threshold_type == "low":
            return f"{var_display} below low threshold: {value:.2f}{unit_display} < {threshold:.2f}{unit_display}"
        else:
            return f"{var_display} above high threshold: {value:.2f}{unit_display} > {threshold:.2f}{unit_display}"
