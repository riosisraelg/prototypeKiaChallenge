# Alarm Simulator Module

## Overview

The `alarm_simulator.py` module detects when variable values exceed configured alarm thresholds and calculates alarm severity based on the percentage of exceedance.

## Features

- **Threshold Detection**: Detects when values exceed `alarm_low` or `alarm_high` thresholds
- **Severity Calculation**: 
  - `warning`: exceedance < 10%
  - `critical`: exceedance ≥ 10%
- **Alarm Metadata**: Generates comprehensive alarm information for MQTT payloads
- **Statistics Tracking**: Tracks total alarms, warnings, and critical alarms

## Usage

### Basic Usage

```python
from alarm_simulator import AlarmSimulator
from data_generator import DataGenerator
from config_loader import ConfigLoader

# Load variables
loader = ConfigLoader()
variables = loader.load_all()

# Create instances
generator = DataGenerator()
alarm_sim = AlarmSimulator()

# Generate data point
variable = variables["PT-001"]
data_point = generator.generate_value(variable)

# Check for alarm
alarm_info = alarm_sim.check_alarm(data_point, variable)

if alarm_info.is_alarm:
    print(f"ALARM: {alarm_info.severity.value}")
    print(f"Message: {alarm_info.message}")
    print(f"Exceedance: {alarm_info.exceedance_percent:.1f}%")
```

### Enriching Data Points

The `enrich_data_point` method adds alarm information to data points for MQTT publishing:

```python
# Enrich data point with alarm information
enriched_payload = alarm_sim.enrich_data_point(data_point, variable)

# The payload now includes alarm metadata
print(enriched_payload)
# {
#   "variable_id": "PT-001",
#   "area": "pre-treatment",
#   "value": 64.0,
#   "timestamp": "2024-01-15T10:30:00.000Z",
#   "unit": "°C",
#   "quality": "good",
#   "metadata": {...},
#   "alarm": {
#     "is_alarm": true,
#     "severity": "critical",
#     "threshold_type": "low",
#     "threshold_value": 65.0,
#     "exceedance_percent": 20.0,
#     "message": "Temperature below low threshold: 64.00 < 65.00 °C"
#   }
# }
```

### Integration with MQTT Publisher

```python
from mqtt_publisher import MQTTPublisher
from alarm_simulator import AlarmSimulator
from data_generator import DataGenerator
from config_loader import ConfigLoader

# Initialize components
loader = ConfigLoader()
variables = loader.load_all()
generator = DataGenerator()
alarm_sim = AlarmSimulator()
mqtt = MQTTPublisher(config)

# Connect to MQTT broker
mqtt.connect()

# Generate and publish data with alarm information
for variable in variables.values():
    # Generate data point
    data_point = generator.generate_value(variable)
    
    # Enrich with alarm information
    enriched_payload = alarm_sim.enrich_data_point(data_point, variable)
    
    # Publish to MQTT
    topic = f"kia/paintshop/{variable.area}/{variable.variable_id}"
    mqtt.publish(topic, enriched_payload)

# Get alarm statistics
stats = alarm_sim.get_statistics()
print(f"Total alarms: {stats['total_alarms']}")
print(f"Warnings: {stats['warnings']}")
print(f"Critical: {stats['critical']}")
```

## Alarm Severity Calculation

The severity is calculated based on how far the value exceeds the threshold relative to the available range:

### Low Alarms (value < alarm_low)

```
available_range = alarm_low - min_range
exceedance = alarm_low - value
exceedance_percent = (exceedance / available_range) * 100
```

### High Alarms (value > alarm_high)

```
available_range = max_range - alarm_high
exceedance = value - alarm_high
exceedance_percent = (exceedance / available_range) * 100
```

### Severity Determination

- **Warning**: `exceedance_percent < 10%`
- **Critical**: `exceedance_percent >= 10%`

## Example Scenarios

### Scenario 1: Warning Low Alarm

```
Variable: Temperature
min_range: 60.0°C
alarm_low: 65.0°C
alarm_high: 75.0°C
max_range: 80.0°C

Current value: 64.6°C

Calculation:
- available_range = 65.0 - 60.0 = 5.0
- exceedance = 65.0 - 64.6 = 0.4
- exceedance_percent = (0.4 / 5.0) * 100 = 8%

Result: WARNING (8% < 10%)
```

### Scenario 2: Critical High Alarm

```
Variable: Voltage
min_range: 240.0V
alarm_low: 245.0V
alarm_high: 285.0V
max_range: 290.0V

Current value: 286.0V

Calculation:
- available_range = 290.0 - 285.0 = 5.0
- exceedance = 286.0 - 285.0 = 1.0
- exceedance_percent = (1.0 / 5.0) * 100 = 20%

Result: CRITICAL (20% >= 10%)
```

## API Reference

### AlarmSimulator Class

#### Methods

- `check_alarm(data_point: DataPoint, variable: Variable) -> AlarmInfo`
  - Checks if a data point triggers an alarm condition
  - Returns AlarmInfo with alarm status and details

- `enrich_data_point(data_point: DataPoint, variable: Variable) -> Dict[str, Any]`
  - Enriches a data point with alarm information
  - Returns dictionary ready for MQTT publishing

- `get_statistics() -> Dict[str, int]`
  - Returns alarm statistics (total_alarms, warnings, critical)

- `reset_statistics() -> None`
  - Resets alarm counters to zero

### AlarmInfo Class

#### Attributes

- `is_alarm: bool` - Whether an alarm condition exists
- `severity: Optional[AlarmSeverity]` - Alarm severity (WARNING or CRITICAL)
- `threshold_type: Optional[str]` - Type of threshold exceeded ("low" or "high")
- `threshold_value: Optional[float]` - The threshold value that was exceeded
- `exceedance_percent: Optional[float]` - Percentage of exceedance
- `message: Optional[str]` - Human-readable alarm message

#### Methods

- `to_dict() -> Dict[str, Any]` - Converts to dictionary for JSON serialization

### AlarmSeverity Enum

- `WARNING = "warning"` - Exceedance < 10%
- `CRITICAL = "critical"` - Exceedance ≥ 10%

## Testing

Run the built-in test:

```bash
cd simulator
python alarm_simulator.py
```

Run unit tests:

```bash
pytest tests/unit/test_alarm_simulator.py -v
```

## Requirements Validation

This module validates the following requirements:

- **Requirement 1.5**: Generates alarm events when variables exceed configured thresholds
- **Requirement 4.2**: Generates alarms with severity levels (warning, critical) based on threshold exceedance

## Related Modules

- `config_loader.py` - Loads variable configurations with alarm thresholds
- `data_generator.py` - Generates data points that may trigger alarms
- `mqtt_publisher.py` - Publishes enriched data with alarm information to IoT Core
