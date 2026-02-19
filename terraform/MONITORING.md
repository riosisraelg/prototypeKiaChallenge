# CloudWatch and SNS Monitoring Configuration

## Overview

This document describes the CloudWatch and SNS monitoring infrastructure for the KIA Paint Shop IoT Prototype. The monitoring setup is designed to provide observability while minimizing costs, with a focus on detecting issues early and preventing budget overruns.

## Components

### 1. CloudWatch Log Groups

Log groups are pre-created for all Lambda functions with a 7-day retention period to balance observability with cost containment.

**Lambda Functions with Log Groups:**
- `kia-paintshop-prototype-ingest` - Data ingestion from IoT Core
- `kia-paintshop-prototype-process` - Anomaly detection and alarm generation
- `kia-paintshop-prototype-statistics` - Statistical calculations
- `kia-paintshop-prototype-api-list-variables` - API: List variables
- `kia-paintshop-prototype-api-get-variable-data` - API: Get variable data
- `kia-paintshop-prototype-api-list-alarms` - API: List alarms
- `kia-paintshop-prototype-api-acknowledge-alarm` - API: Acknowledge alarm
- `kia-paintshop-prototype-api-get-statistics` - API: Get statistics

**Configuration:**
- Retention: 7 days (configurable via `cloudwatch_log_retention_days` variable)
- Naming pattern: `/aws/lambda/{project_name}-{function_name}`
- Automatic cleanup after retention period

### 2. SNS Topic for Notifications

An SNS topic is created for alarm notifications. This is optional and can be configured with email subscriptions if needed.

**Topic Details:**
- Name: `kia-paintshop-prototype-alarms`
- Encryption: AWS managed KMS key (alias/aws/sns)
- Policy: Allows CloudWatch to publish alarm notifications

**Email Subscription (Optional):**
To receive email notifications, uncomment the `aws_sns_topic_subscription` resource in `monitoring.tf` and set your email address:

```hcl
resource "aws_sns_topic_subscription" "alarms_email" {
  topic_arn = aws_sns_topic.alarms.arn
  protocol  = "email"
  endpoint  = "your-email@example.com"
}
```

**Note:** Email subscriptions require confirmation. You'll receive a confirmation email from AWS SNS that must be confirmed before notifications are delivered.

### 3. CloudWatch Alarms

#### Cost Monitoring Alarms

**Estimated Charges Alarm:**
- Triggers when estimated AWS charges exceed $20 USD (configurable)
- Evaluation: Every 6 hours
- Purpose: Early warning to prevent budget overruns
- Action: Sends notification to SNS topic

#### Service Usage Limit Alarms

**IoT Core Messages:**
- Threshold: 13,333 messages/day (~400K/month, 80% of free tier)
- Free tier limit: 500K messages/month
- Purpose: Prevent exceeding free tier and incurring charges
- Metric: `PublishIn.Success` in `AWS/IoT` namespace

**DynamoDB Storage:**
- Threshold: 80% utilization
- Free tier limit: 25GB
- Purpose: Monitor storage usage approaching free tier limit
- Metric: `AccountProvisionedReadCapacityUtilization` in `AWS/DynamoDB` namespace

**Lambda Invocations:**
- Threshold: 26,666 invocations/day (~800K/month, 80% of free tier)
- Free tier limit: 1M invocations/month
- Purpose: Prevent exceeding free tier
- Metric: `Invocations` in `AWS/Lambda` namespace

#### Lambda Error Rate Alarms

**Ingest Lambda Errors:**
- Threshold: >5% error rate
- Evaluation: 2 consecutive periods of 5 minutes
- Purpose: Detect data ingestion issues
- Calculation: `(Errors / Invocations) * 100`

**Process Lambda Errors:**
- Threshold: >5% error rate
- Evaluation: 2 consecutive periods of 5 minutes
- Purpose: Detect processing and anomaly detection issues
- Calculation: `(Errors / Invocations) * 100`

#### Lambda Performance Alarms

**API Lambda Latency:**
- Threshold: >2 seconds average duration
- Evaluation: 2 consecutive periods of 5 minutes
- Purpose: Detect performance degradation in API responses
- Metric: `Duration` in `AWS/Lambda` namespace

### 4. CloudWatch Dashboard

A CloudWatch dashboard is created to visualize key metrics in one place.

**Dashboard Widgets:**

1. **IoT Core Messages** - Total messages published to IoT Core
2. **Lambda Invocations & Errors** - Lambda execution metrics
3. **DynamoDB Capacity Usage** - Read/write capacity consumption
4. **Estimated AWS Charges** - Current month's estimated charges
5. **Custom Application Metrics** - Application-specific metrics (messages processed, alarms generated)

**Access:**
- Dashboard name: `kia-paintshop-prototype-dashboard`
- URL: Available in AWS Console → CloudWatch → Dashboards

### 5. Custom Metrics Namespace

**Namespace:** `KIA/PaintShop`

This namespace is reserved for application-specific custom metrics that will be sent by Lambda functions.

**Planned Custom Metrics:**
- `MessagesProcessed` - Count of successfully processed messages
- `AlarmsGenerated` - Count of alarms generated
- `UnexpectedErrors` - Count of unexpected errors
- `StatisticsCalculated` - Count of statistics calculations performed

**Dimensions:**
- `FunctionName` - Lambda function name
- `Operation` - Specific operation being performed
- `Status` - Success/failure status
- `Area` - Paint shop area (pre-treatment, e-coat, production-control)

## Cost Considerations

### CloudWatch Costs

**Log Storage:**
- First 5GB/month: Free
- Expected usage: ~2GB/month with 7-day retention
- Cost: $0 (within free tier)

**Custom Metrics:**
- First 10 metrics: Free
- Expected usage: ~50 custom metrics
- Cost: ~$0.40/month ($0.01 per metric beyond free tier)

**Alarms:**
- First 10 alarms: Free
- Created alarms: 8 alarms
- Cost: $0 (within free tier)

**Dashboard:**
- First 3 dashboards: Free
- Created dashboards: 1
- Cost: $0 (within free tier)

**Total Estimated CloudWatch Cost:** ~$0.40/month

### SNS Costs

**Notifications:**
- First 1,000 email notifications: Free
- Expected usage: <100 notifications/month
- Cost: $0 (within free tier)

**Total Estimated SNS Cost:** $0/month

### Total Monitoring Cost

**Estimated Total:** ~$0.40/month

## Configuration Variables

The following Terraform variables control monitoring behavior:

```hcl
variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period (days)"
  type        = number
  default     = 7
}

variable "cost_alert_threshold_usd" {
  description = "Cost alert threshold in USD"
  type        = number
  default     = 20
}

variable "budget_limit_usd" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 50
}
```

## Usage

### Viewing Logs

**Via AWS Console:**
1. Navigate to CloudWatch → Log groups
2. Select the log group for the Lambda function
3. View log streams

**Via AWS CLI:**
```bash
# List log groups
aws logs describe-log-groups --log-group-name-prefix /aws/lambda/kia-paintshop

# Tail logs for a specific function
aws logs tail /aws/lambda/kia-paintshop-prototype-ingest --follow

# Query logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/kia-paintshop-prototype-ingest \
  --filter-pattern "ERROR"
```

### Viewing Alarms

**Via AWS Console:**
1. Navigate to CloudWatch → Alarms
2. View alarm status and history

**Via AWS CLI:**
```bash
# List all alarms
aws cloudwatch describe-alarms --alarm-name-prefix kia-paintshop

# Get alarm history
aws cloudwatch describe-alarm-history \
  --alarm-name kia-paintshop-prototype-estimated-charges-alarm
```

### Viewing Dashboard

**Via AWS Console:**
1. Navigate to CloudWatch → Dashboards
2. Select `kia-paintshop-prototype-dashboard`

**Dashboard URL:**
```
https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=kia-paintshop-prototype-dashboard
```

### Viewing Custom Metrics

**Via AWS CLI:**
```bash
# List custom metrics
aws cloudwatch list-metrics --namespace KIA/PaintShop

# Get metric statistics
aws cloudwatch get-metric-statistics \
  --namespace KIA/PaintShop \
  --metric-name MessagesProcessed \
  --start-time 2024-01-01T00:00:00Z \
  --end-time 2024-01-02T00:00:00Z \
  --period 3600 \
  --statistics Sum
```

## Troubleshooting

### Alarms Not Triggering

1. **Check alarm state:**
   ```bash
   aws cloudwatch describe-alarms --alarm-names kia-paintshop-prototype-estimated-charges-alarm
   ```

2. **Verify metrics are being published:**
   ```bash
   aws cloudwatch list-metrics --namespace AWS/Lambda
   ```

3. **Check SNS topic subscriptions:**
   ```bash
   aws sns list-subscriptions-by-topic --topic-arn <sns-topic-arn>
   ```

### Not Receiving Email Notifications

1. **Confirm SNS subscription:**
   - Check your email for confirmation message from AWS SNS
   - Click the confirmation link

2. **Check spam folder:**
   - SNS emails may be filtered as spam

3. **Verify subscription status:**
   ```bash
   aws sns list-subscriptions-by-topic --topic-arn <sns-topic-arn>
   ```
   - Status should be "Confirmed"

### High CloudWatch Costs

1. **Check log retention:**
   - Ensure retention is set to 7 days
   - Delete old log groups if needed

2. **Review custom metrics:**
   - Limit custom metrics to essential ones
   - Use dimensions efficiently

3. **Optimize log verbosity:**
   - Reduce DEBUG level logging in production
   - Use structured logging to minimize log size

## Cleanup

When running `terraform destroy`, all monitoring resources will be automatically deleted:

- CloudWatch log groups (and all log data)
- CloudWatch alarms
- CloudWatch dashboard
- SNS topic and subscriptions

**Note:** Log data is permanently deleted and cannot be recovered after destruction.

## Best Practices

1. **Log Retention:**
   - Keep retention at 7 days for cost optimization
   - Export important logs to S3 for long-term storage if needed

2. **Alarm Thresholds:**
   - Adjust thresholds based on actual usage patterns
   - Set alarms at 80% of limits to allow time for action

3. **Custom Metrics:**
   - Use dimensions to organize metrics
   - Batch metric submissions to reduce API calls
   - Only publish metrics for significant events

4. **SNS Notifications:**
   - Keep email subscriptions optional to avoid notification fatigue
   - Consider using SMS or Lambda for critical alerts only

5. **Dashboard:**
   - Customize dashboard widgets based on monitoring needs
   - Add widgets for specific troubleshooting scenarios

## References

- [CloudWatch Pricing](https://aws.amazon.com/cloudwatch/pricing/)
- [SNS Pricing](https://aws.amazon.com/sns/pricing/)
- [CloudWatch Logs Insights Query Syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/CWL_QuerySyntax.html)
- [CloudWatch Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)
