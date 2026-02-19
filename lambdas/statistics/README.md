# Statistics Lambda Function

## Overview

This Lambda function calculates statistical metrics for sensor data on a scheduled basis. It is triggered by EventBridge every 5 minutes to compute sliding window statistics for all active variables.

## Functionality

### Main Process

1. **Retrieve Active Variables**: Queries DynamoDB to get all active variables
2. **Query Sensor Data**: For each variable, retrieves data from the last 10 minutes
3. **Calculate Statistics**: Computes average, min, max, and standard deviation
4. **Store Results**: Saves statistics to DynamoDB with 7-day TTL
5. **Register Metrics**: Sends custom metrics to CloudWatch

### Statistics Calculated

- **Average (avg)**: Mean value of all data points
- **Minimum (min)**: Lowest value in the window
- **Maximum (max)**: Highest value in the window
- **Standard Deviation (stddev)**: Sample standard deviation (N-1)

### Validation

- Requires minimum 3 data points for valid statistics
- Handles missing data gracefully (stores count=0)
- Validates against NaN and infinite values

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SENSOR_DATA_TABLE` | `kia-paintshop-sensor-data` | DynamoDB table with sensor data |
| `STATISTICS_TABLE` | `kia-paintshop-statistics` | DynamoDB table for statistics |
| `VARIABLES_METADATA_TABLE` | `kia-paintshop-variables-metadata` | DynamoDB table with variable metadata |
| `WINDOW_MINUTES` | `10` | Time window for statistics (minutes) |
| `TTL_DAYS` | `7` | TTL for statistics records (days) |
| `LOG_LEVEL` | `INFO` | Logging level |

## DynamoDB Schema

### Input: sensor-data Table

```
PK: "{area}#{variable_id}"
SK: "DATA#{timestamp_ms}"
value: number
timestamp: string (ISO 8601)
```

### Output: statistics Table

```
PK: "{variable_id}"
SK: "STATS#{window_start}"
variable_id: string
area: string
window_start: string (ISO 8601)
window_end: string (ISO 8601)
window_minutes: number
count: number
avg: number (if valid)
min: number (if valid)
max: number (if valid)
stddev: number (if valid)
is_valid: boolean
ttl: number (epoch seconds)
```

## CloudWatch Metrics

### Success Metrics

- `StatisticsCalculated`: Count of successful calculations
- `DataPointsProcessed`: Number of data points processed per variable
- `VariablesProcessed`: Total variables processed
- `SuccessfulCalculations`: Count of successful variable calculations

### Error Metrics

- `InsufficientDataPoints`: Variables with < 3 data points
- `NoDataPoints`: Variables with no data in window
- `StatisticsErrors`: Errors during calculation/storage
- `FailedCalculations`: Count of failed variable calculations
- `UnexpectedErrors`: Unexpected errors
- `HandlerErrors`: Handler-level errors

### Performance Metrics

- `ProcessingTimeMs`: Total processing time in milliseconds

## Trigger

**EventBridge Rule**: Scheduled expression `rate(5 minutes)`

## IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Scan",
        "dynamodb:Query",
        "dynamodb:PutItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/kia-paintshop-sensor-data",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-statistics",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-variables-metadata"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Configuration

### Lambda Settings

- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Architecture**: arm64 (Graviton2 for cost optimization)

### Dependencies

See `requirements.txt`:
- `boto3`: AWS SDK
- `numpy`: Numerical calculations

## Error Handling

### Retry Logic

- DynamoDB throttling: Exponential backoff (1s, 2s, 4s)
- Maximum 3 retry attempts per operation
- Failed items logged but don't block other variables

### Graceful Degradation

- Missing metadata: Skip variable, log warning
- No data points: Store count=0, mark as invalid
- Calculation errors: Store error message, continue processing

## Testing

### Unit Tests

```bash
pytest tests/unit/test_statistics_handler.py -v
```

### Property-Based Tests

```bash
pytest tests/property/test_properties_statistics.py -v
```

### Local Testing

```python
import json
from handler import handler

# Mock context
class Context:
    request_id = "test-request-id"

# Mock event (EventBridge scheduled event)
event = {
    "version": "0",
    "id": "test-event-id",
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "time": "2024-01-15T10:30:00Z"
}

# Invoke handler
result = handler(event, Context())
print(json.dumps(result, indent=2))
```

## Monitoring

### Key Metrics to Watch

1. **SuccessfulCalculations**: Should match number of active variables
2. **InsufficientDataPoints**: High values indicate data ingestion issues
3. **ProcessingTimeMs**: Should stay well below 60s timeout
4. **StatisticsErrors**: Should be near zero

### Alarms

Recommended CloudWatch Alarms:

- `StatisticsErrors > 10` in 5 minutes
- `ProcessingTimeMs > 50000` (50 seconds)
- `FailedCalculations > 5` in 5 minutes

## Performance Considerations

### Optimization

- Uses batch operations where possible
- Queries only necessary time windows
- Efficient numpy calculations
- Parallel processing potential (future enhancement)

### Scalability

- Current: ~100 variables, 5-minute intervals
- Estimated processing time: 5-10 seconds for 100 variables
- Can scale to 500+ variables with current configuration

### Cost Optimization

- 7-day TTL reduces storage costs
- Efficient queries minimize RCU consumption
- Arm64 architecture reduces compute costs by ~20%

## Requirements Validation

**Validates Requirements:**
- 4.1: Calculate sliding window statistics (average, min, max) for last 10 minutes
- 5.5: Return aggregated statistics for last 24 hours

## Related Components

- `statistics_calculator.py`: Core calculation logic
- `lambdas/ingest/handler.py`: Ingests sensor data
- `lambdas/process/handler.py`: Processes alarms
- `tests/property/test_properties_statistics.py`: Property-based tests
