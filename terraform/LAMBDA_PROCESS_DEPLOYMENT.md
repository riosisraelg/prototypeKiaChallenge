# Lambda Process Function - Deployment Guide

## Overview

This document describes the deployment configuration for the Lambda Process function, which detects anomalies in sensor data and generates alarms when thresholds are exceeded.

## Function Details

- **Function Name**: `kia-paintshop-demo-process`
- **Runtime**: Python 3.11
- **Memory**: 512 MB
- **Timeout**: 60 seconds
- **Handler**: `handler.handler`

## Architecture

```
EventBridge (paintshop-event-bus)
    ↓ (Sensor Data Received events)
Lambda Process
    ↓ (reads metadata)
DynamoDB variables-metadata
    ↓ (writes alarms)
DynamoDB alarms
    ↓ (metrics)
CloudWatch Metrics
```

## Trigger Configuration

The Lambda is triggered by EventBridge events from the ingest Lambda:

- **Event Bus**: `kia-paintshop-demo-event-bus`
- **Event Pattern**:
  ```json
  {
    "source": ["kia.paintshop.ingest"],
    "detail-type": ["Sensor Data Received"]
  }
  ```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `ALARMS_TABLE` | DynamoDB table for storing alarms | `kia-paintshop-demo-alarms` |
| `VARIABLES_METADATA_TABLE` | DynamoDB table with variable metadata | `kia-paintshop-demo-variables-metadata` |
| `LOG_LEVEL` | Logging level | `INFO` |

## IAM Permissions

The Lambda function requires the following permissions:

### DynamoDB Read (Variables Metadata)
- `dynamodb:GetItem` - Read variable metadata
- `dynamodb:Query` - Query metadata table

### DynamoDB Write (Alarms)
- `dynamodb:PutItem` - Create new alarm records
- `dynamodb:UpdateItem` - Update alarm status

### CloudWatch
- `logs:CreateLogStream` - Create log streams
- `logs:PutLogEvents` - Write logs
- `cloudwatch:PutMetricData` - Send custom metrics to KIA/PaintShop namespace

### SQS
- `sqs:SendMessage` - Send failed messages to DLQ

## Processing Logic

1. **Receive Event**: EventBridge event with sensor data
2. **Retrieve Metadata**: Get variable thresholds from DynamoDB
3. **Detect Anomaly**: Compare value against alarm_low and alarm_high
4. **Calculate Severity**:
   - `warning`: Exceeds threshold by <10%
   - `critical`: Exceeds threshold by ≥10%
5. **Store Alarm**: If anomaly detected, create record in alarms table
6. **Send Metrics**: Report processing metrics to CloudWatch

## Alarm Record Structure

```json
{
  "PK": "ALARM#{uuid}",
  "SK": "METADATA",
  "alarm_id": "uuid",
  "variable_id": "PT-TEMP-001",
  "area": "pre-treatment",
  "severity": "warning",
  "status": "active",
  "message": "Temperature exceeds high threshold",
  "value": 68.5,
  "threshold": 68.0,
  "threshold_type": "high",
  "exceedance_percent": 0.74,
  "created_at": "2024-01-15T10:30:00.000Z",
  "sensor_timestamp": "2024-01-15T10:30:00.000Z",
  "variable_name": "Pre-Treatment Temperature"
}
```

## CloudWatch Metrics

The function publishes the following custom metrics to the `KIA/PaintShop` namespace:

| Metric | Description | Unit | Dimensions |
|--------|-------------|------|------------|
| `AlarmsGenerated` | Number of alarms created | Count | - |
| `AlarmsBySeverity` | Alarms by severity level | Count | Severity |
| `AlarmsByArea` | Alarms by area | Count | Area |
| `ProcessingTimeMs` | Processing duration | Milliseconds | - |
| `DataPointsProcessed` | Data points processed without alarm | Count | - |
| `ProcessingErrors` | Processing errors | Count | - |
| `MetadataNotFound` | Variables without metadata | Count | - |
| `NoThresholds` | Variables without thresholds | Count | - |
| `AlarmStorageErrors` | Errors storing alarms | Count | - |
| `ProcessErrors` | Permanent processing errors | Count | - |
| `UnexpectedErrors` | Unexpected errors | Count | - |

## CloudWatch Alarms

The following CloudWatch Alarms are configured:

1. **DLQ Messages** (`lambda-process-dlq`)
   - Threshold: >10 messages
   - Period: 5 minutes
   - Action: SNS notification

2. **Lambda Errors** (`lambda-process-errors`)
   - Threshold: >5 errors in 10 minutes
   - Period: 5 minutes
   - Action: SNS notification

3. **Lambda Duration** (`lambda-process-duration`)
   - Threshold: >50 seconds (approaching 60s timeout)
   - Period: 5 minutes
   - Action: SNS notification

4. **High Alarm Rate** (`high-alarm-rate`)
   - Threshold: >50 alarms in 10 minutes
   - Period: 5 minutes
   - Action: SNS notification

## Error Handling

### Validation Errors (400)
- Missing required fields
- Returns error response, no retry

### Metadata Not Found
- Variable has no metadata in DynamoDB
- Logs warning, skips anomaly detection
- Returns success (no alarm generated)

### No Thresholds Defined
- Variable metadata exists but no alarm thresholds
- Logs warning, skips anomaly detection
- Returns success (no alarm generated)

### DynamoDB Throttling (503)
- Retries up to 3 times with exponential backoff (1s, 2s, 4s)
- If all retries fail, raises ProcessError
- Message sent to DLQ for later processing

### Permanent Errors (500)
- Table not found
- Invalid data
- Raises ProcessError, no retry
- Message sent to DLQ

### Unexpected Errors
- Logs full stack trace
- Re-raises exception to trigger Lambda retry
- After 3 Lambda retries, message sent to DLQ

## Deployment Steps

### 1. Package Lambda Function

Terraform automatically packages the Lambda function from `lambdas/process/`:

```bash
cd terraform
terraform init
```

The `archive_file` data source creates a ZIP file containing:
- `handler.py` - Main Lambda handler
- `anomaly_detector.py` - Anomaly detection logic

### 2. Deploy Infrastructure

```bash
terraform plan
terraform apply
```

This creates:
- Lambda function
- IAM role and policies
- CloudWatch Log Group
- EventBridge rule and target
- SQS Dead Letter Queue
- CloudWatch Alarms

### 3. Verify Deployment

```bash
# Check Lambda function exists
aws lambda get-function --function-name kia-paintshop-demo-process

# Check EventBridge rule
aws events describe-rule \
  --name kia-paintshop-demo-process-sensor-data \
  --event-bus-name kia-paintshop-demo-event-bus

# Check CloudWatch Log Group
aws logs describe-log-groups \
  --log-group-name-prefix /aws/lambda/kia-paintshop-demo-process
```

### 4. Test Function

Test with a sample event:

```bash
aws lambda invoke \
  --function-name kia-paintshop-demo-process \
  --payload '{
    "detail": {
      "variable_id": "PT-TEMP-001",
      "area": "pre-treatment",
      "value": 70.0,
      "timestamp": "2024-01-15T10:30:00.000Z",
      "unit": "°C"
    }
  }' \
  response.json

cat response.json
```

## Monitoring

### View Logs

```bash
# Stream logs in real-time
aws logs tail /aws/lambda/kia-paintshop-demo-process --follow

# View recent logs
aws logs tail /aws/lambda/kia-paintshop-demo-process --since 1h
```

### Check Metrics

```bash
# View alarms generated
aws cloudwatch get-metric-statistics \
  --namespace KIA/PaintShop \
  --metric-name AlarmsGenerated \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# View processing time
aws cloudwatch get-metric-statistics \
  --namespace KIA/PaintShop \
  --metric-name ProcessingTimeMs \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average,Maximum
```

### Check DLQ

```bash
# Check DLQ message count
aws sqs get-queue-attributes \
  --queue-url $(aws sqs get-queue-url --queue-name kia-paintshop-demo-process-dlq --query 'QueueUrl' --output text) \
  --attribute-names ApproximateNumberOfMessages
```

## Troubleshooting

### No Alarms Being Generated

1. Check if events are reaching the Lambda:
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-demo-process --since 10m
   ```

2. Verify EventBridge rule is enabled:
   ```bash
   aws events describe-rule \
     --name kia-paintshop-demo-process-sensor-data \
     --event-bus-name kia-paintshop-demo-event-bus
   ```

3. Check if variables have metadata with thresholds:
   ```bash
   aws dynamodb get-item \
     --table-name kia-paintshop-demo-variables-metadata \
     --key '{"PK": {"S": "VAR#PT-TEMP-001"}, "SK": {"S": "METADATA"}}'
   ```

### High Error Rate

1. Check CloudWatch Logs for error messages
2. Review DLQ for failed messages
3. Verify DynamoDB tables exist and have correct permissions
4. Check if Lambda has sufficient memory/timeout

### DynamoDB Throttling

1. Check if on-demand billing is enabled (should be)
2. Review CloudWatch metrics for throttling
3. Consider adding exponential backoff (already implemented)

## Cost Optimization

- **Memory**: 512 MB is sufficient for anomaly detection
- **Timeout**: 60 seconds allows for retries with backoff
- **Billing Mode**: DynamoDB on-demand prevents throttling
- **Log Retention**: 7 days balances observability and cost
- **DLQ Retention**: 14 days for troubleshooting

## Security Considerations

- **Least Privilege**: IAM role has minimal required permissions
- **Encryption**: DynamoDB tables use encryption at rest
- **Network**: Lambda runs in AWS managed VPC
- **Secrets**: No secrets required (uses IAM roles)

## Related Documentation

- [Lambda Ingest Configuration](LAMBDA_INGEST_CONFIGURATION.md)
- [Lambda Statistics Deployment](LAMBDA_STATISTICS_DEPLOYMENT.md)
- [DynamoDB Tables](DYNAMODB_TABLES.md)
- [IoT Lambda Connection](IOT_LAMBDA_CONNECTION_VERIFICATION.md)
