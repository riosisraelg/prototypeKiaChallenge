# KIA Paint Shop IoT Prototype - CloudWatch and SNS Monitoring Configuration

# ============================================================================
# CloudWatch Log Groups for Lambda Functions
# ============================================================================

# Log group for Ingest Lambda
resource "aws_cloudwatch_log_group" "lambda_ingest" {
  name              = "/aws/lambda/${var.project_name}-ingest"
  retention_in_days = var.cloudwatch_log_retention_days

  tags = {
    Name        = "${var.project_name}-lambda-ingest-logs"
    Description = "Logs for data ingestion Lambda function"
  }
}

# Note: Log groups for Process and Statistics Lambdas are defined in their respective .tf files
# - lambda_process.tf defines aws_cloudwatch_log_group.lambda_process
# - lambda_statistics.tf defines aws_cloudwatch_log_group.lambda_statistics
# - lambda_api.tf defines all API Lambda log groups

# ============================================================================
# SNS Topic for Notifications (Optional - for cost containment)
# ============================================================================

# SNS topic for alarm notifications
resource "aws_sns_topic" "alarms" {
  name              = "${var.project_name}-alarms"
  display_name      = "KIA Paint Shop Prototype Alarms"
  kms_master_key_id = "alias/aws/sns"

  tags = {
    Name        = "${var.project_name}-alarms-topic"
    Description = "SNS topic for CloudWatch alarm notifications"
  }
}

# SNS topic policy to allow CloudWatch to publish
resource "aws_sns_topic_policy" "alarms" {
  arn = aws_sns_topic.alarms.arn

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudWatchToPublish"
        Effect = "Allow"
        Principal = {
          Service = "cloudwatch.amazonaws.com"
        }
        Action   = "SNS:Publish"
        Resource = aws_sns_topic.alarms.arn
      }
    ]
  })
}

# Optional: SNS email subscription (commented out to avoid requiring email confirmation)
# Uncomment and set email address if notifications are needed
# resource "aws_sns_topic_subscription" "alarms_email" {
#   topic_arn = aws_sns_topic.alarms.arn
#   protocol  = "email"
#   endpoint  = "your-email@example.com"
# }

# ============================================================================
# CloudWatch Alarms for Cost Monitoring
# ============================================================================

# Alarm for estimated charges exceeding threshold
resource "aws_cloudwatch_metric_alarm" "estimated_charges" {
  alarm_name          = "${var.project_name}-estimated-charges-alarm"
  alarm_description   = "Alert when estimated AWS charges exceed ${var.cost_alert_threshold_usd} USD"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "EstimatedCharges"
  namespace           = "AWS/Billing"
  period              = 21600 # 6 hours
  statistic           = "Maximum"
  threshold           = var.cost_alert_threshold_usd
  treat_missing_data  = "notBreaching"

  dimensions = {
    Currency = "USD"
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-estimated-charges-alarm"
    Description = "Monitors estimated AWS charges"
  }
}

# ============================================================================
# CloudWatch Alarms for Service Usage Limits
# ============================================================================

# Alarm for IoT Core message count approaching free tier limit
# Free tier: 500K messages/month, alert at 400K (80%)
resource "aws_cloudwatch_metric_alarm" "iot_messages_high" {
  alarm_name          = "${var.project_name}-iot-messages-high"
  alarm_description   = "Alert when IoT Core messages approach free tier limit (400K/month)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "PublishIn.Success"
  namespace           = "AWS/IoT"
  period              = 86400 # 1 day
  statistic           = "Sum"
  threshold           = 13333 # ~400K/month = 13,333/day
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-iot-messages-alarm"
    Description = "Monitors IoT Core message volume"
  }
}

# Alarm for DynamoDB storage approaching free tier limit
# Free tier: 25GB, alert at 20GB (80%)
# Note: DynamoDB storage metrics are not directly available in CloudWatch
# This alarm monitors consumed capacity as a proxy for storage usage
resource "aws_cloudwatch_metric_alarm" "dynamodb_storage_high" {
  alarm_name          = "${var.project_name}-dynamodb-storage-high"
  alarm_description   = "Alert when DynamoDB consumed write capacity is high (proxy for storage growth)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "ConsumedWriteCapacityUnits"
  namespace           = "AWS/DynamoDB"
  period              = 3600 # 1 hour
  statistic           = "Sum"
  threshold           = 10000 # High write activity indicates rapid storage growth
  treat_missing_data  = "notBreaching"

  dimensions = {
    TableName = "${var.project_name}-sensor-data"
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-dynamodb-storage-alarm"
    Description = "Monitors DynamoDB write activity as proxy for storage growth"
  }
}

# Alarm for Lambda invocations approaching free tier limit
# Free tier: 1M invocations/month, alert at 800K (80%)
resource "aws_cloudwatch_metric_alarm" "lambda_invocations_high" {
  alarm_name          = "${var.project_name}-lambda-invocations-high"
  alarm_description   = "Alert when Lambda invocations approach free tier limit (800K/month)"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "Invocations"
  namespace           = "AWS/Lambda"
  period              = 86400 # 1 day
  statistic           = "Sum"
  threshold           = 26666 # ~800K/month = 26,666/day
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-lambda-invocations-alarm"
    Description = "Monitors Lambda invocation count"
  }
}

# ============================================================================
# CloudWatch Alarms for Lambda Error Rates
# ============================================================================

# Alarm for high error rate in Ingest Lambda (>5%)
resource "aws_cloudwatch_metric_alarm" "lambda_ingest_errors" {
  alarm_name          = "${var.project_name}-lambda-ingest-errors"
  alarm_description   = "Alert when Ingest Lambda error rate exceeds 5%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "(errors / invocations) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-ingest"
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-ingest"
      }
    }
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-lambda-ingest-errors-alarm"
    Description = "Monitors Ingest Lambda error rate"
  }
}

# Alarm for high error rate in Process Lambda (>5%)
resource "aws_cloudwatch_metric_alarm" "lambda_process_errors" {
  alarm_name          = "${var.project_name}-lambda-process-errors"
  alarm_description   = "Alert when Process Lambda error rate exceeds 5%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "(errors / invocations) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-process"
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-process"
      }
    }
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-lambda-process-errors-alarm"
    Description = "Monitors Process Lambda error rate"
  }
}

# Alarm for high error rate in Statistics Lambda (>5%)
resource "aws_cloudwatch_metric_alarm" "lambda_statistics_errors" {
  alarm_name          = "${var.project_name}-lambda-statistics-errors"
  alarm_description   = "Alert when Statistics Lambda error rate exceeds 5%"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  threshold           = 5
  treat_missing_data  = "notBreaching"

  metric_query {
    id          = "error_rate"
    expression  = "(errors / invocations) * 100"
    label       = "Error Rate (%)"
    return_data = true
  }

  metric_query {
    id = "errors"
    metric {
      metric_name = "Errors"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-statistics"
      }
    }
  }

  metric_query {
    id = "invocations"
    metric {
      metric_name = "Invocations"
      namespace   = "AWS/Lambda"
      period      = 300 # 5 minutes
      stat        = "Sum"
      dimensions = {
        FunctionName = "${var.project_name}-statistics"
      }
    }
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-lambda-statistics-errors-alarm"
    Description = "Monitors Statistics Lambda error rate"
  }
}

# ============================================================================
# CloudWatch Alarms for Lambda Performance
# ============================================================================

# Alarm for high latency in API Lambdas (>2 seconds)
resource "aws_cloudwatch_metric_alarm" "lambda_api_latency" {
  alarm_name          = "${var.project_name}-lambda-api-latency"
  alarm_description   = "Alert when API Lambda duration exceeds 2 seconds"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = 300 # 5 minutes
  statistic           = "Average"
  threshold           = 2000 # 2 seconds in milliseconds
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = "${var.project_name}-api-list-variables"
  }

  alarm_actions = [aws_sns_topic.alarms.arn]

  tags = {
    Name        = "${var.project_name}-lambda-api-latency-alarm"
    Description = "Monitors API Lambda latency"
  }
}

# ============================================================================
# CloudWatch Dashboard (Optional - for visualization)
# ============================================================================

resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/IoT", "PublishIn.Success", { stat = "Sum", label = "IoT Messages" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "IoT Core Messages"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", { stat = "Sum", label = "Total Invocations" }],
            [".", "Errors", { stat = "Sum", label = "Errors" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Lambda Invocations & Errors"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", { stat = "Sum" }],
            [".", "ConsumedWriteCapacityUnits", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "DynamoDB Capacity Usage"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Billing", "EstimatedCharges", { stat = "Maximum", label = "Estimated Charges (USD)" }]
          ]
          period = 21600
          stat   = "Maximum"
          region = "us-east-1" # Billing metrics are only in us-east-1
          title  = "Estimated AWS Charges"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      },
      {
        type = "metric"
        properties = {
          metrics = [
            ["KIA/PaintShop", "MessagesProcessed", { stat = "Sum" }],
            [".", "AlarmsGenerated", { stat = "Sum" }]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Custom Application Metrics"
          yAxis = {
            left = {
              min = 0
            }
          }
        }
      }
    ]
  })

  depends_on = [
    aws_cloudwatch_log_group.lambda_ingest
  ]
}

# ============================================================================
# Outputs
# ============================================================================
# Note: Outputs are defined in outputs.tf to avoid duplication

