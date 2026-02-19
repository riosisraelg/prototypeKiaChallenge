# Lambda Process Function

This Lambda function processes sensor data events to detect anomalies and generate alarms based on configured thresholds.

## Components

### anomaly_detector.py

Detects when sensor values exceed alarm thresholds and calculates alarm severity.

**Features:**
- Compares current value with alarm thresholds (alarm_low, alarm_high)
- Calculates percentage of excess to determine severity
- Returns alarm with metadata (severity, message, threshold)
- Severity levels:
  - **warning**: exceedance < 10%
  - **critical**: exceedance ≥ 10%

**Usage:**

```python
from anomaly_detector import AnomalyDetector

detector = AnomalyDetector()

result = detector.detect(
    value=72.0,
    alarm_low=60.0,
    alarm_high=70.0,
    min_range=50.0,
    max_range=80.0,
    variable_name="PT-TEMP-001",
    unit="°C"
)

if result.is_alarm:
    print(f"Alarm detected: {result.severity.value}")
    print(f"Message: {result.message}")
    print(f"Exceedance: {result.exceedance_percent:.1f}%")
```

**Exceedance Calculation:**

For **low alarms** (value < alarm_low):
```
exceedance_percent = (alarm_low - value) / (alarm_low - min_range) * 100
```

For **high alarms** (value > alarm_high):
```
exceedance_percent = (value - alarm_high) / (max_range - alarm_high) * 100
```

**Example:**
- Value: 72°C
- Alarm high: 70°C
- Max range: 80°C
- Exceedance: (72 - 70) / (80 - 70) * 100 = 20%
- Severity: CRITICAL (≥10%)

## Requirements Validation

This module validates:
- **Requirement 4.2**: Detect when variables exceed defined thresholds and generate alarms with severity levels
- **Requirement 4.4**: Register anomaly events with context (previous values, timestamp, affected variable)

## Testing

Run unit tests:
```bash
python -m pytest tests/unit/test_anomaly_detector.py -v
```

## Integration

The anomaly detector will be used by the Lambda process handler (handler.py) to:
1. Receive sensor data events from EventBridge
2. Extract value and threshold information
3. Detect anomalies using the detector
4. Store alarms in DynamoDB if detected
5. Publish notifications for critical alarms
