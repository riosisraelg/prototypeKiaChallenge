# KIA Paint Shop IoT Prototype - Deployment Instructions

## Overview

This document provides step-by-step instructions for deploying the Lambda ingest function that was configured in Task 6.5.

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** configured with valid credentials
2. **Terraform** >= 1.5.0 installed
3. **AWS Account** with appropriate permissions
4. **Existing Infrastructure** from Tasks 1-5 (DynamoDB tables, IoT Core, S3, CloudWatch)

## Deployment Steps

### Step 1: Review Configuration

Navigate to the terraform directory and review the Lambda configuration:

```bash
cd terraform
cat lambda_ingest.tf
```

Key configuration points:
- Runtime: Python 3.11
- Memory: 256 MB
- Timeout: 30 seconds
- Handler: `handler.handler`
- DLQ: Configured with 14-day retention

### Step 2: Initialize Terraform

If not already initialized, run:

```bash
terraform init
```

This will download the `archive` provider needed to package the Lambda function.

### Step 3: Validate Configuration

Validate the Terraform configuration:

```bash
terraform validate
```

Expected output: `Success! The configuration is valid.`

### Step 4: Review Planned Changes

Generate and review the execution plan:

```bash
terraform plan -out=tfplan
```

Expected new resources:
- `aws_cloudwatch_event_bus.paintshop` - EventBridge event bus
- `aws_sqs_queue.lambda_ingest_dlq` - Dead letter queue
- `aws_iam_role.lambda_ingest` - Lambda execution role
- `aws_iam_role_policy.lambda_ingest` - IAM policy
- `aws_lambda_function.ingest` - Lambda function
- `aws_lambda_permission.allow_iot` - IoT invoke permission
- `aws_cloudwatch_metric_alarm.lambda_ingest_dlq` - DLQ alarm

### Step 5: Apply Configuration

Apply the Terraform configuration:

```bash
terraform apply tfplan
```

This will:
1. Create the EventBridge event bus
2. Create the SQS DLQ
3. Create the IAM role and policy
4. Package the Lambda code from `lambdas/ingest/`
5. Deploy the Lambda function
6. Configure IoT Core permissions
7. Create CloudWatch alarms

### Step 6: Verify Deployment

After successful deployment, verify the resources:

#### 6.1 Check Lambda Function

```bash
aws lambda get-function --function-name kia-paintshop-prototype-ingest
```

Expected: Function details with status "Active"

#### 6.2 Check IAM Role

```bash
aws iam get-role --role-name kia-paintshop-prototype-lambda-ingest-role
```

Expected: Role details with Lambda trust policy

#### 6.3 Check EventBridge Bus

```bash
aws events describe-event-bus --name kia-paintshop-prototype-event-bus
```

Expected: Event bus details

#### 6.4 Check DLQ

```bash
# Get DLQ URL from Terraform output
terraform output lambda_ingest_dlq_url

# Check DLQ attributes
aws sqs get-queue-attributes \
  --queue-url $(terraform output -raw lambda_ingest_dlq_url) \
  --attribute-names All
```

Expected: Queue with 14-day retention

#### 6.5 View Terraform Outputs

```bash
terraform output
```

Expected outputs:
- `lambda_ingest_arn`
- `lambda_ingest_name`
- `eventbridge_bus_name`
- `eventbridge_bus_arn`
- `lambda_ingest_dlq_url`
- `lambda_ingest_dlq_arn`

## Testing the Lambda Function

### Test 1: Direct Lambda Invocation

Create a test payload file:

```bash
cat > test_payload.json << 'EOF'
{
  "variable_id": "PT-TEMP-001",
  "area": "pre-treatment",
  "timestamp": "2024-01-15T10:30:00Z",
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
EOF
```

Invoke the Lambda function:

```bash
aws lambda invoke \
  --function-name kia-paintshop-prototype-ingest \
  --payload file://test_payload.json \
  --cli-binary-format raw-in-base64-out \
  response.json

# View response
cat response.json | jq .
```

Expected response:
```json
{
  "statusCode": 200,
  "body": "{\"success\": true, \"data\": {...}, \"request_id\": \"...\", \"processing_time_ms\": ...}"
}
```

### Test 2: Check CloudWatch Logs

View Lambda execution logs:

```bash
aws logs tail /aws/lambda/kia-paintshop-prototype-ingest --follow
```

Expected: Log entries showing message processing

### Test 3: Verify DynamoDB Storage

Check if data was stored in DynamoDB:

```bash
aws dynamodb query \
  --table-name kia-paintshop-prototype-sensor-data \
  --key-condition-expression "PK = :pk" \
  --expression-attribute-values '{":pk":{"S":"pre-treatment#PT-TEMP-001"}}' \
  --limit 5
```

Expected: Items with the test data

### Test 4: End-to-End Test via IoT Core

If the simulator is running, publish a message via IoT Core:

```bash
aws iot-data publish \
  --topic "kia/paintshop/pre-treatment/PT-TEMP-001" \
  --payload file://test_payload.json \
  --cli-binary-format raw-in-base64-out
```

Then verify:
1. Lambda was invoked (check CloudWatch Logs)
2. Data was stored in DynamoDB
3. Event was published to EventBridge (check Lambda logs)

## Monitoring

### CloudWatch Metrics

View Lambda metrics in CloudWatch:

```bash
# Invocations
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=kia-paintshop-prototype-ingest \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum

# Errors
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Errors \
  --dimensions Name=FunctionName,Value=kia-paintshop-prototype-ingest \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Sum
```

### CloudWatch Alarms

Check alarm status:

```bash
# Lambda error rate alarm
aws cloudwatch describe-alarms \
  --alarm-names kia-paintshop-prototype-lambda-ingest-errors

# DLQ alarm
aws cloudwatch describe-alarms \
  --alarm-names kia-paintshop-prototype-lambda-ingest-dlq
```

### DLQ Monitoring

Check for messages in DLQ:

```bash
aws sqs get-queue-attributes \
  --queue-url $(terraform output -raw lambda_ingest_dlq_url) \
  --attribute-names ApproximateNumberOfMessages
```

If messages are in DLQ, retrieve them:

```bash
aws sqs receive-message \
  --queue-url $(terraform output -raw lambda_ingest_dlq_url) \
  --max-number-of-messages 10
```

## Troubleshooting

### Issue: Lambda Not Invoked by IoT Rule

**Symptoms**: Messages published to IoT Core but Lambda not invoked

**Solutions**:
1. Check IoT Rule is enabled:
   ```bash
   aws iot get-topic-rule --rule-name kia_paintshop_prototype_ingest_rule
   ```

2. Verify Lambda permission:
   ```bash
   aws lambda get-policy --function-name kia-paintshop-prototype-ingest
   ```

3. Check IoT Rule error logs:
   ```bash
   aws logs tail /aws/iot/rules/kia-paintshop-prototype --follow
   ```

### Issue: Lambda Errors

**Symptoms**: Lambda invoked but returns errors

**Solutions**:
1. Check CloudWatch Logs:
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-prototype-ingest --follow
   ```

2. Check for validation errors in logs
3. Verify payload format matches expected schema
4. Check DynamoDB table exists and is accessible

### Issue: DynamoDB Write Failures

**Symptoms**: Lambda executes but data not in DynamoDB

**Solutions**:
1. Verify IAM permissions:
   ```bash
   aws iam get-role-policy \
     --role-name kia-paintshop-prototype-lambda-ingest-role \
     --policy-name kia-paintshop-prototype-lambda-ingest-policy
   ```

2. Check table exists:
   ```bash
   aws dynamodb describe-table \
     --table-name kia-paintshop-prototype-sensor-data
   ```

3. Check for throttling in CloudWatch metrics

### Issue: EventBridge Publish Failures

**Symptoms**: Data stored but EventBridge events not published

**Solutions**:
1. Check EventBridge bus exists:
   ```bash
   aws events describe-event-bus \
     --name kia-paintshop-prototype-event-bus
   ```

2. Verify IAM permissions for `events:PutEvents`
3. Check Lambda logs for EventBridge errors

## Cost Monitoring

After deployment, monitor costs:

```bash
# Check estimated charges
aws cloudwatch get-metric-statistics \
  --namespace AWS/Billing \
  --metric-name EstimatedCharges \
  --dimensions Name=Currency,Value=USD \
  --start-time $(date -u -d '7 days ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 86400 \
  --statistics Maximum
```

Expected costs for Lambda ingest:
- **Lambda Invocations**: $0 (within 1M free tier)
- **Lambda Duration**: $0 (within 400K GB-seconds free tier)
- **EventBridge**: $0 (included)
- **SQS DLQ**: $0 (within 1M requests free tier)

## Next Steps

After successful deployment and testing:

1. **Task 6.6**: Verify IoT Rule connection (already configured)
2. **Task 7**: Implement Lambda process function
3. **Task 8**: Implement Lambda statistics function
4. **Task 9**: Checkpoint - Test complete data pipeline

## Rollback

If you need to rollback the Lambda deployment:

```bash
cd terraform

# Destroy only Lambda resources (not recommended, use with caution)
terraform destroy -target=aws_lambda_function.ingest

# Or destroy all new resources
terraform destroy
```

**Warning**: This will delete the Lambda function and all associated resources. Data in DynamoDB will be preserved.

## Summary

Task 6.5 is complete when:
- ✅ Lambda function deployed with Python 3.11 runtime
- ✅ Memory configured to 256 MB
- ✅ Timeout set to 30 seconds
- ✅ IAM role created with minimum privileges
- ✅ Environment variables configured (DYNAMODB_TABLE, EVENTBRIDGE_BUS)
- ✅ DLQ configured with SQS
- ✅ CloudWatch Logs integration working
- ✅ CloudWatch Alarms created
- ✅ IoT Core can invoke Lambda
- ✅ Test invocation successful
- ✅ Data stored in DynamoDB
- ✅ Events published to EventBridge

The Lambda ingest function is now ready to receive and process IoT sensor data!
