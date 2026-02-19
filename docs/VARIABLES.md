# Variable Configuration Guide

This document describes the 100 variables monitored in the KIA Paint Shop IoT Prototype.

## Overview

The prototype monitors **97 actual variables** from CSV files plus **3 additional production control variables** for a total of 100 variables across three paint shop areas.

## Variable Categories

### 1. Pre-Treatment (PT) - 48 Variables

Variables from the pre-treatment stage where metal surfaces are cleaned and prepared for painting.

**Source:** `KMX-PA-PT-F-001.csv`

**Variable Types:**
- Temperature sensors (°C)
- pH levels
- Concentration measurements (g/L, %)
- Flow rates (L/min)
- Pressure sensors (bar)
- Tank levels (%)

**Example Variables:**
- `PT_TEMP_TANK_1` - Pre-treatment tank 1 temperature
- `PT_PH_DEGREASER` - Degreaser pH level
- `PT_CONC_PHOSPHATE` - Phosphate concentration
- `PT_FLOW_RINSE_1` - Rinse water flow rate
- `PT_PRESSURE_SPRAY` - Spray pressure

**Typical Ranges:**
- Temperature: 20-80°C
- pH: 2-12
- Concentration: 0-100 g/L
- Flow: 0-500 L/min
- Pressure: 0-10 bar

**Alarm Thresholds:**
- Configured per variable in CSV
- Typically ±10% of normal operating range
- Critical alarms at ±20%

---

### 2. E-Coat (ED) - 18 Variables

Variables from the electrodeposition coating stage where paint is applied electrically.

**Source:** `KMX-PA-PE-F-001.csv`

**Variable Types:**
- Voltage (V)
- Current (A)
- Temperature (°C)
- Bath composition (%)
- Coating thickness (μm)
- Conductivity (μS/cm)

**Example Variables:**
- `ED_VOLTAGE_MAIN` - Main electrodeposition voltage
- `ED_CURRENT_ANODE` - Anode current
- `ED_TEMP_BATH` - Bath temperature
- `ED_THICKNESS_COATING` - Coating thickness
- `ED_CONDUCTIVITY` - Bath conductivity

**Typical Ranges:**
- Voltage: 200-400V
- Current: 0-100A
- Temperature: 25-35°C
- Thickness: 15-25 μm
- Conductivity: 800-1500 μS/cm

**Alarm Thresholds:**
- Voltage: ±5% (critical for quality)
- Temperature: ±2°C
- Thickness: ±2 μm
- Other parameters: ±10%

---

### 3. Production Control - 34 Variables

Additional variables for production monitoring and control (31 from config + 3 synthetic).

**Source:** Configured in `simulator/config.yaml`

**Variable Types:**
- Line speed (m/min)
- Cycle time (seconds)
- Reject count (units)
- Energy consumption (kWh)
- Production count (units)
- Quality metrics (%)
- Equipment status (0-100%)

**Example Variables:**
- `PROD_LINE_SPEED` - Conveyor line speed
- `PROD_CYCLE_TIME` - Average cycle time
- `PROD_REJECT_COUNT` - Rejected units count
- `PROD_ENERGY_CONSUMPTION` - Power consumption
- `PROD_QUALITY_SCORE` - Overall quality score
- `PROD_OEE` - Overall Equipment Effectiveness

**Typical Ranges:**
- Line speed: 1-10 m/min
- Cycle time: 60-300 seconds
- Reject count: 0-50 units/hour
- Energy: 100-500 kWh
- Quality: 85-100%
- OEE: 70-95%

**Alarm Thresholds:**
- Line speed: ±15%
- Quality score: <90%
- Reject count: >20 units/hour
- OEE: <75%

---

## CSV File Structure

### Pre-Treatment CSV (KMX-PA-PT-F-001.csv)

```csv
Variable_ID,Variable_Name,Unit,Min_Range,Max_Range,Alarm_Low,Alarm_High,Area
PT_001,Temperature Tank 1,°C,20,80,25,75,pre-treatment
PT_002,pH Degreaser,pH,2,12,3,11,pre-treatment
...
```

**Columns:**
- `Variable_ID` - Unique identifier (e.g., PT_001)
- `Variable_Name` - Human-readable name
- `Unit` - Measurement unit
- `Min_Range` - Minimum valid value
- `Max_Range` - Maximum valid value
- `Alarm_Low` - Low alarm threshold
- `Alarm_High` - High alarm threshold
- `Area` - Process area (pre-treatment)

### E-Coat CSV (KMX-PA-PE-F-001.csv)

```csv
Variable_ID,Variable_Name,Unit,Min_Range,Max_Range,Alarm_Low,Alarm_High,Area
ED_001,Main Voltage,V,200,400,220,380,e-coat
ED_002,Anode Current,A,0,100,5,95,e-coat
...
```

**Same structure as Pre-Treatment CSV**

---

## Configuration in Simulator

### config.yaml Structure

```yaml
mqtt:
  host: "your-iot-endpoint.iot.us-east-1.amazonaws.com"
  port: 8883
  client_id: "kia-paintshop-simulator"
  
variables:
  csv_files:
    - "KMX-PA-PT-F-001.csv"
    - "KMX-PA-PE-F-001.csv"
  
  additional_variables:
    - id: "PROD_LINE_SPEED"
      name: "Line Speed"
      unit: "m/min"
      min_range: 1.0
      max_range: 10.0
      alarm_low: 2.0
      alarm_high: 9.0
      area: "production-control"
    # ... more variables

simulation:
  interval_seconds: 30
  anomaly_probability: 0.05  # 5% chance of anomaly
```

---

## Variable Naming Convention

### Format: `{AREA}_{TYPE}_{LOCATION}_{NUMBER}`

**Examples:**
- `PT_TEMP_TANK_1` - Pre-Treatment Temperature Tank 1
- `ED_VOLTAGE_MAIN` - E-Coat Main Voltage
- `PROD_LINE_SPEED` - Production Line Speed

**Area Codes:**
- `PT` - Pre-Treatment
- `ED` - E-Coat (Electrodeposition)
- `PROD` - Production Control

**Type Codes:**
- `TEMP` - Temperature
- `PH` - pH Level
- `CONC` - Concentration
- `FLOW` - Flow Rate
- `PRESSURE` - Pressure
- `VOLTAGE` - Voltage
- `CURRENT` - Current
- `THICKNESS` - Coating Thickness

---

## Data Generation

### Normal Operation

The simulator generates values within the `Min_Range` to `Max_Range` using:
- Gaussian distribution centered at midpoint
- Standard deviation = (Max - Min) / 6
- Ensures 99.7% of values within range

### Anomaly Generation

With 5% probability, the simulator generates anomalies:
- **Low anomaly:** Value below `Alarm_Low`
- **High anomaly:** Value above `Alarm_High`
- **Severity calculation:**
  - Warning: Exceeds threshold by <10%
  - Critical: Exceeds threshold by ≥10%

### Example:
```python
Variable: PT_TEMP_TANK_1
Min: 20°C, Max: 80°C
Alarm_Low: 25°C, Alarm_High: 75°C

Normal: 45-55°C (most common)
Warning: 23-25°C or 75-77°C
Critical: <23°C or >77°C
```

---

## MQTT Topic Structure

Each variable publishes to its own topic:

```
kia/paintshop/{area}/{variable_id}
```

**Examples:**
- `kia/paintshop/pre-treatment/PT_TEMP_TANK_1`
- `kia/paintshop/e-coat/ED_VOLTAGE_MAIN`
- `kia/paintshop/production-control/PROD_LINE_SPEED`

---

## Message Payload Format

```json
{
  "variable_id": "PT_TEMP_TANK_1",
  "variable_name": "Temperature Tank 1",
  "area": "pre-treatment",
  "value": 52.3,
  "unit": "°C",
  "timestamp": "2026-02-19T12:30:00Z",
  "min_range": 20.0,
  "max_range": 80.0,
  "alarm_low": 25.0,
  "alarm_high": 75.0,
  "has_alarm": false,
  "alarm_severity": null,
  "metadata": {
    "simulator_version": "1.0.0",
    "message_id": "uuid-here"
  }
}
```

---

## DynamoDB Storage

### sensor-data Table

**Partition Key:** `variable_id` (e.g., "PT_TEMP_TANK_1")  
**Sort Key:** `timestamp` (ISO 8601 string)

**Attributes:**
- `variable_id` - Variable identifier
- `timestamp` - Measurement timestamp
- `value` - Measured value (Number)
- `unit` - Measurement unit
- `area` - Process area
- `variable_name` - Human-readable name
- `ttl` - Expiration timestamp (30 days)

**GSI: area-timestamp-index**
- Partition Key: `area`
- Sort Key: `timestamp`
- Enables queries by area and time range

---

## API Access

### GET /variables

Returns all 100 variables with metadata:

```json
{
  "success": true,
  "data": {
    "variables": [
      {
        "variable_id": "PT_TEMP_TANK_1",
        "variable_name": "Temperature Tank 1",
        "area": "pre-treatment",
        "unit": "°C",
        "min_range": 20.0,
        "max_range": 80.0,
        "alarm_low": 25.0,
        "alarm_high": 75.0
      },
      // ... 99 more variables
    ],
    "total_count": 100,
    "by_area": {
      "pre-treatment": 48,
      "e-coat": 18,
      "production-control": 34
    }
  }
}
```

### GET /variables/{id}/data

Returns historical data for a specific variable:

```json
{
  "success": true,
  "data": {
    "variable_id": "PT_TEMP_TANK_1",
    "data_points": [
      {
        "timestamp": "2026-02-19T12:00:00Z",
        "value": 52.3,
        "unit": "°C"
      },
      // ... more data points
    ],
    "count": 120,
    "time_range": {
      "start": "2026-02-19T10:00:00Z",
      "end": "2026-02-19T12:00:00Z"
    }
  }
}
```

---

## Adding New Variables

### Option 1: Add to CSV

1. Edit `KMX-PA-PT-F-001.csv` or `KMX-PA-PE-F-001.csv`
2. Add new row with all required columns
3. Restart simulator

### Option 2: Add to config.yaml

```yaml
additional_variables:
  - id: "NEW_VAR_001"
    name: "New Variable Name"
    unit: "unit"
    min_range: 0.0
    max_range: 100.0
    alarm_low: 10.0
    alarm_high: 90.0
    area: "production-control"
```

### Option 3: Update variables-metadata Table

Manually insert into DynamoDB `variables-metadata` table via AWS Console or CLI.

---

## Variable Limits

**Maximum Variables:** 100 (prototype constraint)

**Current Usage:**
- Pre-Treatment: 48 variables
- E-Coat: 18 variables
- Production Control: 34 variables
- **Total: 100 variables**

**To add more variables:**
1. Remove existing variables from CSV/config
2. Or increase the 100-variable limit (requires architecture review)

---

## Troubleshooting

### Variable not appearing in dashboard

1. Check CSV file has correct format
2. Verify variable_id is unique
3. Restart simulator
4. Check CloudWatch Logs for validation errors

### Incorrect alarm thresholds

1. Verify `alarm_low` < `alarm_high`
2. Ensure thresholds are within `min_range` to `max_range`
3. Check simulator logs for threshold violations

### Missing data in API

1. Verify simulator is running
2. Check IoT Core message delivery (CloudWatch Metrics)
3. Verify Lambda ingestion is working (CloudWatch Logs)
4. Check DynamoDB table for data

---

## Best Practices

1. **Naming:** Use consistent naming convention (AREA_TYPE_LOCATION)
2. **Ranges:** Set realistic min/max based on actual equipment
3. **Alarms:** Set thresholds at ±10% of normal operating range
4. **Units:** Use standard SI units when possible
5. **Documentation:** Document each variable's purpose and normal range

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0
