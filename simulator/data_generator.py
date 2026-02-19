"""
Data generator module for KIA Paint Shop IoT Prototype.

This module generates realistic data values within specified ranges,
creates ISO 8601 timestamps, and simulates anomalies.

Features:
- Generate random values within min/max ranges
- ISO 8601 timestamp generation with timezone
- Anomaly simulation with configurable probability
- Metadata inclusion (ranges, alarm thresholds)
"""

import random
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

from config_loader import Variable

logger = logging.getLogger(__name__)


@dataclass
class DataPoint:
    """Represents a single data point for a variable."""
    
    variable_id: str
    area: str
    timestamp: str  # ISO 8601 format
    value: float
    unit: str
    quality: str  # good, bad, uncertain
    metadata: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class DataGenerator:
    """Generates realistic data for process variables."""
    
    def __init__(self, anomaly_probability: float = 0.05):
        """
        Initialize the data generator.
        
        Args:
            anomaly_probability: Probability of generating an anomaly (0.0 to 1.0)
        """
        self.anomaly_probability = anomaly_probability
        self.last_values: Dict[str, float] = {}  # Track last value for smooth transitions
        
    def generate_value(self, variable: Variable, force_anomaly: bool = False) -> DataPoint:
        """
        Generate a data point for a variable.
        
        Args:
            variable: Variable configuration
            force_anomaly: Force generation of an anomalous value
            
        Returns:
            DataPoint with generated value
        """
        # Determine if this should be an anomaly
        is_anomaly = force_anomaly or (random.random() < self.anomaly_probability)
        
        # Generate value
        if is_anomaly:
            value = self._generate_anomalous_value(variable)
            quality = "uncertain"
        else:
            value = self._generate_normal_value(variable)
            quality = "good"
        
        # Store last value for next generation
        self.last_values[variable.variable_id] = value
        
        # Generate timestamp
        timestamp = self._generate_timestamp()
        
        # Create data point
        data_point = DataPoint(
            variable_id=variable.variable_id,
            area=variable.area,
            timestamp=timestamp,
            value=value,
            unit=variable.unit,
            quality=quality,
            metadata={
                "min_range": variable.min_range,
                "max_range": variable.max_range,
                "alarm_low": variable.alarm_low,
                "alarm_high": variable.alarm_high
            }
        )
        
        return data_point
    
    def _generate_normal_value(self, variable: Variable) -> float:
        """
        Generate a normal value within the variable's range.
        
        Uses the last value to create smooth transitions (if available).
        
        Args:
            variable: Variable configuration
            
        Returns:
            Generated value within normal range
        """
        # Get last value if available
        last_value = self.last_values.get(variable.variable_id)
        
        if last_value is not None:
            # Generate value close to last value for smooth transitions
            # Allow up to 10% change from last value
            range_span = variable.max_range - variable.min_range
            max_change = range_span * 0.1
            
            # Random walk
            change = random.uniform(-max_change, max_change)
            new_value = last_value + change
            
            # Clamp to valid range
            new_value = max(variable.min_range, min(variable.max_range, new_value))
        else:
            # First value - generate randomly within range
            # Prefer values in the middle 80% of the range (avoid edges)
            range_span = variable.max_range - variable.min_range
            middle_start = variable.min_range + (range_span * 0.1)
            middle_end = variable.max_range - (range_span * 0.1)
            
            new_value = random.uniform(middle_start, middle_end)
        
        # Round to reasonable precision based on range
        precision = self._determine_precision(variable)
        new_value = round(new_value, precision)
        
        return new_value
    
    def _generate_anomalous_value(self, variable: Variable) -> float:
        """
        Generate an anomalous value that may exceed alarm thresholds.
        
        Args:
            variable: Variable configuration
            
        Returns:
            Generated anomalous value
        """
        # Decide type of anomaly
        anomaly_type = random.choice(['low', 'high', 'extreme_low', 'extreme_high'])
        
        range_span = variable.max_range - variable.min_range
        
        if anomaly_type == 'low':
            # Value below alarm_low but above min_range
            value = random.uniform(variable.min_range, variable.alarm_low)
        elif anomaly_type == 'high':
            # Value above alarm_high but below max_range
            value = random.uniform(variable.alarm_high, variable.max_range)
        elif anomaly_type == 'extreme_low':
            # Value at or near min_range
            value = random.uniform(variable.min_range, variable.min_range + range_span * 0.05)
        else:  # extreme_high
            # Value at or near max_range
            value = random.uniform(variable.max_range - range_span * 0.05, variable.max_range)
        
        # Round to reasonable precision
        precision = self._determine_precision(variable)
        value = round(value, precision)
        
        return value
    
    def _determine_precision(self, variable: Variable) -> int:
        """
        Determine appropriate decimal precision based on variable range.
        
        Args:
            variable: Variable configuration
            
        Returns:
            Number of decimal places
        """
        range_span = variable.max_range - variable.min_range
        
        if range_span >= 1000:
            return 0  # No decimals for large ranges
        elif range_span >= 100:
            return 1
        elif range_span >= 10:
            return 2
        else:
            return 3  # More precision for small ranges
    
    def _generate_timestamp(self) -> str:
        """
        Generate ISO 8601 timestamp with timezone.
        
        Returns:
            ISO 8601 formatted timestamp string
        """
        # Use current UTC time
        now = datetime.now(timezone.utc)
        
        # Format as ISO 8601 with milliseconds and timezone
        # Example: 2024-01-15T10:30:00.000Z
        timestamp = now.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        return timestamp
    
    def generate_batch(self, variables: list[Variable], force_anomaly_count: int = 0) -> list[DataPoint]:
        """
        Generate data points for multiple variables.
        
        Args:
            variables: List of variables to generate data for
            force_anomaly_count: Number of variables to force anomalies for
            
        Returns:
            List of generated data points
        """
        data_points = []
        
        # Randomly select variables for forced anomalies (use IDs)
        if force_anomaly_count > 0:
            anomaly_var_ids = set(random.sample([v.variable_id for v in variables], 
                                                min(force_anomaly_count, len(variables))))
        else:
            anomaly_var_ids = set()
        
        # Generate data for each variable
        for variable in variables:
            force_anomaly = variable.variable_id in anomaly_var_ids
            data_point = self.generate_value(variable, force_anomaly=force_anomaly)
            data_points.append(data_point)
        
        return data_points
    
    def reset(self):
        """Reset the generator state (clear last values)."""
        self.last_values.clear()
        logger.info("Data generator state reset")


def main():
    """Test the data generator."""
    import sys
    from pathlib import Path
    
    # Add simulator to path
    sys.path.insert(0, str(Path(__file__).parent))
    
    from config_loader import ConfigLoader
    
    logging.basicConfig(level=logging.INFO)
    
    # Load variables
    loader = ConfigLoader()
    variables = loader.load_all()
    
    # Create generator
    generator = DataGenerator(anomaly_probability=0.1)
    
    print(f"\n{'='*60}")
    print(f"Data Generator Test")
    print(f"{'='*60}\n")
    
    # Generate data for first 5 variables
    test_vars = list(variables.values())[:5]
    
    print("Generating 3 rounds of data...\n")
    
    for round_num in range(1, 4):
        print(f"Round {round_num}:")
        print("-" * 60)
        
        data_points = generator.generate_batch(test_vars)
        
        for dp in data_points:
            print(f"{dp.variable_id}: {dp.value:.2f} {dp.unit} (quality: {dp.quality})")
            print(f"  Timestamp: {dp.timestamp}")
            print(f"  Range: [{dp.metadata['min_range']}, {dp.metadata['max_range']}]")
            print(f"  Alarms: [{dp.metadata['alarm_low']:.2f}, {dp.metadata['alarm_high']:.2f}]")
            
            # Check if value is in alarm range
            if dp.value < dp.metadata['alarm_low']:
                print(f"  ⚠️  LOW ALARM!")
            elif dp.value > dp.metadata['alarm_high']:
                print(f"  ⚠️  HIGH ALARM!")
            
            print()
        
        print()


if __name__ == "__main__":
    main()
