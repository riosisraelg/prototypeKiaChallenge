# Lambda Ingest Function - Terraform Configuration

## Overview

This document describes the Terraform configuration for the Lambda ingest function, which is responsible for receiving IoT sensor data, validating it, storing it in DynamoDB, and publishing events to EventBridge for further processing.

## Configuration Summary

### File: `lambda_ingest.tf`

The configuration includes the following resources:

### 1. EventBridge Event Bus
- **Resource**: `aws_cloudwatch_event_bus.paintshop`
- **Name**: `kia-paintshop-prototype-event-bus`
- **Purpose**: Custom event bus for Lambda-to-Lambda communication

### 2. SQS Dead Letter Queue (DLQ)
- **Resource**: `aws_sqs_queue.lambda_ingest_dlq`
- **Name**: `kia-paintshop-prototype-ingest-dlq`
- **Retention**: 14 days (1,209,600 seconds)
- **Purpose**: Store failed messages for analysis and retry

### 3. IAM Role and Policy
- **Role**: `aws_iam_role.lambda_ingest`
- **Name**: `kia-paintshop-prototype-lambda-ingest-role`
- **Permissions** (minimum privilege):
  - **DynamoDB**: `PutItem`, `UpdateItem` on sensor-data table
  - **EventBridge**: `PutEvents` on custom event bus
  - **CloudWatch Logs**: `CreateLogStream`, `PutLogEvents`
  - **CloudWatch Metrics**: `PutMetricData` (namespace: KIA/PaintShop)
  - **SQS**: `SendMessage` to DLQ

### 4. Lambda Function
- **Resource**: `aws_lambda_function.ingest`
- **Name**: `kia-paintshop-prototype-ingest`
- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 30 seconds
- **Handler**: `handler.handler`
- **Source**: `lambdas/ingest/` directory (zipped automatically)

#### Environment Variables
- `DYNAMODB_TABLE`: Name of the sensor-data DynamoDB table
- `EVENTBRIDGE_BUS`: Name of the EventBridge event bus
- `LOG_LEVEL`: Logging level (default: INFO)
- `TTL_DAYS`: TTL for DynamoDB items (default: 30 days)

#### Dead Letter Queue
- Configured to send failed messages to SQS DLQ after Lambda exhausts retries

### 5. Lambda Permission
- **Resource**: `aws_lambda_permission.allow_iot`
- **Purpose**: Allow IoT Core to invoke the Lambda function
- **Principal**: `iot.amazonaws.com`
- **Source ARN**: IoT Topic Rule ARN

### 6. CloudWatch Alarm - DLQ Messages
- **Resource**: `aws_cloudwatch_metric_alarm.lambda_ingest_dlq`
- **Name**: `kia-paintshop-prototype-lambda-ingest-dlq`
- **Threshold**: Alert when DLQ has more than 10 messages
- **Period**: 5 minutes
- **Action**: Publish to SNS topic for notifications

## Integration with Existing Resources

### IoT Core Integration
The Lambda function is already integrated with the existing IoT Topic Rule:
- **IoT Rule**: `kia_paintshop_prototype_ingest_rule` (defined in `iot.tf`)
- **Topic Pattern**: `kia/paintshop/+/+`
- **SQL**: `SELECT topic(3) as area, topic(4) as variable_id, * FROM 'kia/paintshop/+/+' WHERE timestamp IS NOT NULL`

The IoT Rule automatically invokes the Lambda function when messages arrive on matching topics.

### CloudWatch Logs Integration
The Lambda function uses the log group already defined in `monitoring.tf`:
- **Log Group**: `/aws/lambda/kia-paintshop-prototype-ingest`
- **Retention**: 7 days (configurable via `cloudwatch_log_retention_days` variable)

### CloudWatch Alarms Integration
The Lambda error rate alarm is already defined in `monitoring.tf`:
- **Alarm**: `kia-paintshop-prototype-lambda-ingest-errors`
- **Threshold**: Alert when error rate exceeds 5%
- **Evaluation**: 2 periods of 5 minutes each

## Deployment Package

The Lambda deployment package is created automatically using the `archive_file` data source:
- **Source Directory**: `../lambdas/ingest/`
- **Output**: `.terraform/lambda_ingest.zip`
- **Excluded Files**: `__pycache__`, `*.pyc`, `.gitkeep`, `README.md`, `requirements.txt`

### Included Files
- `handler.py` - Main Lambda handler
- `validators.py` - Message validation functions

### Dependencies
The Lambda function uses only AWS SDK (boto3), which is included in the Lambda runtime. No additional dependencies need to be packaged.

## Outputs

The following outputs are added to `outputs.tf`:

```hcl
output "lambda_ingest_arn" {
  description = "Ingest Lambda function ARN"
  value       = aws_lambda_function.ingest.arn
}

output "lambda_ingest_name" {
  description = "Ingest Lambda function name"
  value       = aws_lambda_function.ingest.function_name
}

output "eventbridge_bus_name" {
  description = "EventBridge bus name"
  value       = aws_cloudwatch_event_bus.paintshop.name
}

output "eventbridge_bus_arn" {
  description = "EventBridge bus ARN"
  value       = aws_cloudwatch_event_bus.paintshop.arn
}

output "lambda_ingest_dlq_url" {
  description = "Lambda ingest DLQ URL"
  value       = aws_sqs_queue.lambda_ingest_dlq.url
}

output "lambda_ingest_dlq_arn" {
  description = "Lambda ingest DLQ ARN"
  value       = aws_sqs_queue.lambda_ingest_dlq.arn
}
```

## Verification Steps

After applying the Terraform configuration:

### 1. Verify Lambda Function
```bash
aws lambda get-function --function-name kia-paintshop-prototype-ingest
```

### 2. Verify IAM Role
```bash
aws iam get-role --role-name kia-paintshop-prototype-lambda-ingest-role
```

### 3. Verify EventBridge Bus
```bash
aws events describe-event-bus --name kia-paintshop-prototype-event-bus
```

### 4. Verify DLQ
```bash
aws sqs get-queue-attributes --queue-url <DLQ_URL> --attribute-names All
```

### 5. Test Lambda Invocation
```bash
aws lambda invoke \
  --function-name kia-paintshop-prototype-ingest \
  --payload '{"variable_id":"PT-TEMP-001","area":"pre-treatment","timestamp":"2024-01-15T10:30:00Z","value":65.5,"unit":"°C"}' \
  response.json
```

### 6. Check CloudWatch Logs
```bash
aws logs tail /aws/lambda/kia-paintshop-prototype-ingest --follow
```

### 7. Verify IoT Rule Integration
```bash
# Publish a test message to IoT Core
aws iot-data publish \
  --topic "kia/paintshop/pre-treatment/PT-TEMP-001" \
  --payload '{"variable_id":"PT-TEMP-001","area":"pre-treatment","timestamp":"2024-01-15T10:30:00Z","value":65.5,"unit":"°C"}' \
  --cli-binary-format raw-in-base64-out
```

### 8. Verify DynamoDB Storage
```bash
aws dynamodb scan \
  --table-name kia-paintshop-prototype-sensor-data \
  --limit 10
```

## Cost Considerations

### Lambda Costs
- **Free Tier**: 1M invocations/month, 400K GB-seconds/month
- **Expected Usage**: ~300K invocations/month (30 variables × 12 msgs/hr × 24 hrs × 30 days)
- **Memory**: 256 MB × 30s timeout = 7.5 GB-seconds per invocation
- **Total**: ~2.25M GB-seconds/month (within free tier)
- **Cost**: $0/month (within free tier)

### EventBridge Costs
- **Free Tier**: Included (no separate charge for custom event buses)
- **Cost**: $0/month

### SQS DLQ Costs
- **Free Tier**: 1M requests/month
- **Expected Usage**: Minimal (only failed messages)
- **Cost**: $0/month (within free tier)

### Total Additional Cost
- **Lambda**: $0
- **EventBridge**: $0
- **SQS**: $0
- **Total**: $0/month (all within free tier)

## Security Considerations

### IAM Permissions
- **Minimum Privilege**: Lambda role has only the permissions needed for its specific tasks
- **Resource-Specific**: Permissions are scoped to specific resources (tables, event bus, log group)
- **No Wildcards**: No wildcard permissions except for CloudWatch metrics (required by service)

### Encryption
- **At Rest**: DynamoDB tables use AWS managed encryption
- **In Transit**: All AWS service communication uses TLS 1.2+
- **DLQ**: SQS queue uses AWS managed encryption

### Network
- **VPC**: Lambda runs in AWS managed VPC (no custom VPC needed for this use case)
- **Internet Access**: Not required (all AWS service endpoints are accessible)

## Troubleshooting

### Lambda Not Invoked by IoT Rule
1. Check IoT Rule is enabled: `aws iot get-topic-rule --rule-name kia_paintshop_prototype_ingest_rule`
2. Verify Lambda permission: `aws lambda get-policy --function-name kia-paintshop-prototype-ingest`
3. Check IoT Rule error logs: `aws logs tail /aws/iot/rules/kia-paintshop-prototype --follow`

### Lambda Errors
1. Check CloudWatch Logs: `aws logs tail /aws/lambda/kia-paintshop-prototype-ingest --follow`
2. Check DLQ for failed messages: `aws sqs receive-message --queue-url <DLQ_URL>`
3. Review CloudWatch metrics: Lambda Errors, Duration, Throttles

### DynamoDB Write Failures
1. Check IAM permissions: Verify Lambda role has `dynamodb:PutItem` permission
2. Check table exists: `aws dynamodb describe-table --table-name kia-paintshop-prototype-sensor-data`
3. Check for throttling: Review DynamoDB metrics in CloudWatch

### EventBridge Publish Failures
1. Check IAM permissions: Verify Lambda role has `events:PutEvents` permission
2. Check event bus exists: `aws events describe-event-bus --name kia-paintshop-prototype-event-bus`
3. Review Lambda logs for EventBridge errors

## Next Steps

After this configuration is applied:

1. **Task 6.6**: The IoT Rule is already connected to the Lambda function (configured in `iot.tf`)
2. **Task 7**: Implement Lambda process function to consume EventBridge events
3. **Task 8**: Implement Lambda statistics function
4. **Task 9**: Checkpoint - Verify complete data pipeline

## Requirements Validation

This configuration satisfies the following requirements:

- **Requirement 8.5**: Lambda deployed with Terraform, packaged with dependencies
- **Requirement 10.3**: IAM role with minimum privilege principle
- **Requirement 3.1**: Data stored in DynamoDB with TTL
- **Requirement 3.2**: Proper partition and sort key structure
- **Requirement 4.5**: Retry logic with DLQ for failed messages
- **Requirement 9.1**: CloudWatch metrics integration
- **Requirement 9.2**: CloudWatch Logs integration

## Configuration Complete

The Lambda ingest function is now fully configured in Terraform with:
- ✅ Runtime: Python 3.11
- ✅ Memory: 256 MB
- ✅ Timeout: 30 seconds
- ✅ IAM role with minimum privileges
- ✅ Environment variables configured
- ✅ DLQ configured
- ✅ CloudWatch Logs integration
- ✅ CloudWatch Alarms for monitoring
- ✅ IoT Core integration
- ✅ EventBridge integration
