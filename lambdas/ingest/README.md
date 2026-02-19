# Lambda Ingest Handler

Lambda function for ingesting IoT sensor data from AWS IoT Core.

## Overview

This Lambda function receives events from AWS IoT Rules Engine, validates the payload, enriches it with metadata, stores it in DynamoDB, and publishes events to EventBridge for further processing.

## Requirements

- Requirements: 3.1, 3.2, 4.5
- Python 3.11+
- boto3
- DynamoDB table for sensor data
- EventBridge bus (optional)

## Functionality

### 1. Message Validation
- Validates JSON format
- Validates required fields (variable_id, area, timestamp, value, unit)
- Validates data types and ranges
- Uses `validators.py` module

### 2. Message Enrichment
- Adds `request_id` from Lambda context
- Adds `processing_timestamp` (ISO 8601)
- Adds `ingestion_time_ms` (epoch milliseconds)

### 3. DynamoDB Storage
- Stores data with partition key: `{area}#{variable_id}`
- Stores data with sort key: `DATA#{timestamp_ms}`
- Sets TTL to 30 days from ingestion
- Implements retry logic with exponential backoff

### 4. EventBridge Publishing
- Publishes `SensorDataIngested` events
- Source: `kia.paintshop.ingest`
- Best effort (doesn't fail if EventBridge unavailable)

### 5. Error Handling
- Validation errors return HTTP 400
- Transient errors retry with exponential backoff (max 3 attempts)
- Permanent errors logged and sent to DLQ
- All errors send CloudWatch metrics

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DYNAMODB_TABLE` | DynamoDB table name for sensor data | `kia-paintshop-sensor-data` |
| `EVENTBRIDGE_BUS` | EventBridge bus name | `default` |
| `TTL_DAYS` | TTL in days for DynamoDB items | `30` |
| `LOG_LEVEL` | Logging level (INFO, DEBUG, ERROR) | `INFO` |

## Input Event Format

The Lambda expects events from IoT Rules Engine with the following structure:

```json
{
  "variable_id": "PT-TEMP-001",
  "area": "pre-treatment",
  "timestamp": "2024-01-15T10:30:00.000Z",
  "value": 65.5,
  "unit": "°C",
  "quality": "good",
  "metadata": {
    "min_range": 60.0,
    "max_range": 70.0,
    "alarm_low": 62.0,
    "alarm_high": 68.0
  }
}
```

## Output

### Success Response (HTTP 200)
```json
{
  "statusCode": 200,
  "body": {
    "success": true,
    "data": {
      "variable_id": "PT-TEMP-001",
      "area": "pre-treatment",
      "timestamp": "2024-01-15T10:30:00.000Z",
      "stored": true,
      "eventbridge_published": true
    },
    "request_id": "abc-123-def",
    "processing_time_ms": 45.2
  }
}
```

### Validation Error (HTTP 400)
```json
{
  "statusCode": 400,
  "body": {
    "success": false,
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "Missing required field: timestamp"
    },
    "request_id": "abc-123-def"
  }
}
```

### Internal Error (HTTP 500)
```json
{
  "statusCode": 500,
  "body": {
    "success": false,
    "error": {
      "code": "INGEST_ERROR",
      "message": "Failed to store in DynamoDB"
    },
    "request_id": "abc-123-def"
  }
}
```

## CloudWatch Metrics

The function sends the following custom metrics to CloudWatch namespace `KIA/PaintShop`:

- `MessagesIngested` - Count of successfully ingested messages
- `ValidationErrors` - Count of validation failures
- `DynamoDBErrors` - Count of DynamoDB storage failures
- `EventBridgeErrors` - Count of EventBridge publishing failures
- `IngestErrors` - Count of permanent ingestion errors
- `UnexpectedErrors` - Count of unexpected errors
- `ProcessingTimeMs` - Processing time in milliseconds

## DynamoDB Item Structure

```python
{
  'PK': 'pre-treatment#PT-TEMP-001',
  'SK': 'DATA#1705314600000',
  'variable_id': 'PT-TEMP-001',
  'area': 'pre-treatment',
  'timestamp': '2024-01-15T10:30:00.000Z',
  'value': 65.5,
  'unit': '°C',
  'quality': 'good',
  'request_id': 'abc-123-def',
  'processing_timestamp': '2024-01-15T10:30:01.000Z',
  'ttl': 1707906601,  # 30 days from now
  'metadata': {
    'min_range': 60.0,
    'max_range': 70.0,
    'alarm_low': 62.0,
    'alarm_high': 68.0
  }
}
```

## EventBridge Event Structure

```json
{
  "Source": "kia.paintshop.ingest",
  "DetailType": "SensorDataIngested",
  "Detail": {
    "variable_id": "PT-TEMP-001",
    "area": "pre-treatment",
    "timestamp": "2024-01-15T10:30:00.000Z",
    "value": 65.5,
    "unit": "°C",
    "metadata": {},
    "request_id": "abc-123-def"
  },
  "EventBusName": "default"
}
```

## Error Handling Strategy

### Validation Errors (Permanent)
- Return HTTP 400
- Log with WARNING level
- Send CloudWatch metric
- Do NOT retry

### DynamoDB Throttling (Transient)
- Retry up to 3 times with exponential backoff (1s, 2s, 4s)
- If all retries fail, raise exception to trigger DLQ
- Log with ERROR level

### EventBridge Failures (Non-Critical)
- Retry up to 3 times
- If all retries fail, log warning but continue
- Data is still stored in DynamoDB
- Send CloudWatch metric

### Unexpected Errors
- Log with EXCEPTION level (includes stack trace)
- Send CloudWatch metric
- Re-raise to trigger Lambda retry and DLQ

## Testing

Run unit tests:
```bash
python -m pytest tests/unit/test_ingest_handler.py -v
```

## Deployment

This Lambda is deployed via Terraform. See `terraform/lambda.tf` for configuration.

### IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/kia-paintshop-sensor-data"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "arn:aws:events:*:*:event-bus/default"
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

## Monitoring

### CloudWatch Logs
- Log group: `/aws/lambda/kia-paintshop-ingest`
- Retention: 7 days
- Log level: INFO (configurable via LOG_LEVEL env var)

### CloudWatch Alarms (Recommended)
- Error rate > 5%
- Processing time > 2 seconds
- Validation errors > 100/hour

## Performance

- Memory: 256 MB
- Timeout: 30 seconds
- Typical processing time: 20-50ms
- Cold start: ~500ms

## Limitations

- Maximum payload size: 256 KB (Lambda limit)
- Maximum retries: 3 attempts
- TTL: Fixed at 30 days (configurable via env var)
- EventBridge: Best effort, not guaranteed delivery
