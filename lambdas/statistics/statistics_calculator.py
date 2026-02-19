"""
Statistics calculator module for KIA Paint Shop IoT Prototype.

This module calculates statistical metrics (average, min, max, standard deviation)
for sensor data using numpy for efficient computation.

Features:
- Calculate sliding window statistics for time-series data
- Validate minimum data points requirement (at least 3 points)
- Use numpy for efficient numerical calculations
- Handle edge cases (empty data, insufficient points, invalid values)

Validates Requirements: 4.1, 5.5
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class StatisticsResult:
    """Result of statistical calculations."""
    
    count: int
    avg: Optional[float]
    min: Optional[float]
    max: Optional[float]
    stddev: Optional[float]
    is_valid: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        result = {
            "count": self.count,
            "is_valid": self.is_valid
        }
        
        if self.is_valid:
            result.update({
                "avg": round(self.avg, 2) if self.avg is not None else None,
                "min": round(self.min, 2) if self.min is not None else None,
                "max": round(self.max, 2) if self.max is not None else None,
                "stddev": round(self.stddev, 2) if self.stddev is not None else None
            })
        else:
            result["error_message"] = self.error_message
        
        return result


class StatisticsCalculator:
    """Calculates statistical metrics for sensor data."""
    
    MIN_DATA_POINTS = 3
    
    def calculate(self, values: List[float]) -> StatisticsResult:
        """
        Calculate statistics for a list of sensor values.
        
        Args:
            values: List of numeric sensor values
            
        Returns:
            StatisticsResult with calculated metrics or error information
        """
        # Validate input
        if not values:
            logger.warning("Empty values list provided")
            return StatisticsResult(
                count=0,
                avg=None,
                min=None,
                max=None,
                stddev=None,
                is_valid=False,
                error_message="No data points provided"
            )
        
        # Check minimum data points requirement
        if len(values) < self.MIN_DATA_POINTS:
            logger.warning(f"Insufficient data points: {len(values)} < {self.MIN_DATA_POINTS}")
            return StatisticsResult(
                count=len(values),
                avg=None,
                min=None,
                max=None,
                stddev=None,
                is_valid=False,
                error_message=f"Insufficient data points (minimum {self.MIN_DATA_POINTS} required)"
            )
        
        try:
            # Convert to numpy array for efficient computation
            data = np.array(values, dtype=np.float64)
            
            # Check for NaN or infinite values
            if np.any(np.isnan(data)) or np.any(np.isinf(data)):
                logger.error("Data contains NaN or infinite values")
                return StatisticsResult(
                    count=len(values),
                    avg=None,
                    min=None,
                    max=None,
                    stddev=None,
                    is_valid=False,
                    error_message="Data contains invalid values (NaN or infinite)"
                )
            
            # Calculate statistics using numpy
            avg = float(np.mean(data))
            min_val = float(np.min(data))
            max_val = float(np.max(data))
            stddev = float(np.std(data, ddof=1))  # Sample standard deviation (N-1)
            
            logger.debug(
                f"Calculated statistics: count={len(values)}, avg={avg:.2f}, "
                f"min={min_val:.2f}, max={max_val:.2f}, stddev={stddev:.2f}"
            )
            
            return StatisticsResult(
                count=len(values),
                avg=avg,
                min=min_val,
                max=max_val,
                stddev=stddev,
                is_valid=True
            )
            
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            return StatisticsResult(
                count=len(values),
                avg=None,
                min=None,
                max=None,
                stddev=None,
                is_valid=False,
                error_message=f"Calculation error: {str(e)}"
            )
    
    def calculate_from_data_points(
        self,
        data_points: List[Dict[str, Any]],
        value_key: str = 'value'
    ) -> StatisticsResult:
        """
        Calculate statistics from a list of data point dictionaries.
        
        This is a convenience method for working with DynamoDB query results
        where each item is a dictionary containing a 'value' field.
        
        Args:
            data_points: List of dictionaries containing sensor data
            value_key: Key name for the value field (default: 'value')
            
        Returns:
            StatisticsResult with calculated metrics
        """
        try:
            # Extract values from data points
            values = []
            for point in data_points:
                if value_key in point:
                    value = point[value_key]
                    # Handle both numeric types and Decimal from DynamoDB
                    if isinstance(value, (int, float)):
                        values.append(float(value))
                    else:
                        # Try to convert to float (handles Decimal)
                        values.append(float(value))
            
            if not values:
                logger.warning(f"No valid values found in data points (key: {value_key})")
                return StatisticsResult(
                    count=0,
                    avg=None,
                    min=None,
                    max=None,
                    stddev=None,
                    is_valid=False,
                    error_message=f"No valid values found in data points"
                )
            
            # Calculate statistics using the main method
            return self.calculate(values)
            
        except Exception as e:
            logger.error(f"Error extracting values from data points: {e}")
            return StatisticsResult(
                count=0,
                avg=None,
                min=None,
                max=None,
                stddev=None,
                is_valid=False,
                error_message=f"Error extracting values: {str(e)}"
            )
