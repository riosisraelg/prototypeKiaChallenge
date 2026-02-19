# KIA Paint Shop IoT Prototype - Lambda Statistics Function Configuration

# SQS Dead Letter Queue for Lambda failures
resource "aws_sqs_queue" "lambda_statistics_dlq" {
  name                      = "${var.project_name}-statistics-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "${var.project_name}-statistics-dlq"
  }
}

# IAM Role for Lambda Statistics Function
resource "aws_iam_role" "lambda_statistics" {
  name = "${var.project_name}-lambda-statistics-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM Policy for Lambda Statistics Function
resource "aws_iam_role_policy" "lambda_statistics" {
  name = "${var.project_name}-lambda-statistics-policy"
  role = aws_iam_role.lambda_statistics.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # DynamoDB read permissions for sensor data and variables metadata
      {
        Effect = "Allow"
        Action = [
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:GetItem"
        ]
        Resource = [
          aws_dynamodb_table.sensor_data.arn,
          aws_dynamodb_table.variables_metadata.arn
        ]
      },
      # DynamoDB write permissions for statistics table
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.statistics.arn
      },
      # CloudWatch Logs permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_statistics.arn}:*"
      },
      # CloudWatch Metrics permissions
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
        Condition = {
          StringEquals = {
            "cloudwatch:namespace" = "KIA/PaintShop"
          }
        }
      },
      # SQS DLQ permissions
      {
        Effect = "Allow"
        Action = [
          "sqs:SendMessage"
        ]
        Resource = aws_sqs_queue.lambda_statistics_dlq.arn
      }
    ]
  })
}

# CloudWatch Log Group for Lambda Statistics
resource "aws_cloudwatch_log_group" "lambda_statistics" {
  name              = "/aws/lambda/${var.project_name}-statistics"
  retention_in_days = var.cloudwatch_log_retention_days
}

# Lambda Layer for numpy (required for statistics calculations)
# Note: In production, create a Lambda layer with numpy pre-compiled for Lambda runtime
# For now, we'll package numpy with the function (increases deployment size)
data "archive_file" "lambda_statistics" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/statistics"
  output_path = "${path.module}/.terraform/lambda_statistics.zip"

  excludes = [
    "__pycache__",
    "*.pyc",
    ".gitkeep",
    "README.md",
    "requirements.txt"
  ]
}

# Lambda Function
resource "aws_lambda_function" "statistics" {
  filename         = data.archive_file.lambda_statistics.output_path
  function_name    = "${var.project_name}-statistics"
  role             = aws_iam_role.lambda_statistics.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.lambda_statistics.output_base64sha256

  runtime     = var.lambda_runtime
  memory_size = 512
  timeout     = 60

  # Use arm64 for cost optimization (Graviton2)
  architectures = ["arm64"]

  environment {
    variables = {
      SENSOR_DATA_TABLE        = aws_dynamodb_table.sensor_data.name
      STATISTICS_TABLE         = aws_dynamodb_table.statistics.name
      VARIABLES_METADATA_TABLE = aws_dynamodb_table.variables_metadata.name
      WINDOW_MINUTES           = "10"
      TTL_DAYS                 = var.statistics_ttl_days
      LOG_LEVEL                = "INFO"
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_statistics_dlq.arn
  }

  depends_on = [
    aws_iam_role_policy.lambda_statistics,
    aws_cloudwatch_log_group.lambda_statistics
  ]
}

# EventBridge Rule to trigger Lambda every 5 minutes
resource "aws_cloudwatch_event_rule" "statistics_schedule" {
  name                = "${var.project_name}-statistics-schedule"
  description         = "Trigger statistics calculation every 5 minutes"
  schedule_expression = "rate(5 minutes)"

  tags = {
    Name = "${var.project_name}-statistics-schedule"
  }
}

# EventBridge Target - Lambda Statistics Function
resource "aws_cloudwatch_event_target" "statistics_lambda" {
  rule      = aws_cloudwatch_event_rule.statistics_schedule.name
  target_id = "StatisticsLambda"
  arn       = aws_lambda_function.statistics.arn
}

# Lambda permission for EventBridge to invoke the function
resource "aws_lambda_permission" "allow_eventbridge_statistics" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.statistics.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.statistics_schedule.arn
}

# CloudWatch Alarm for DLQ messages
resource "aws_cloudwatch_metric_alarm" "lambda_statistics_dlq" {
  alarm_name          = "${var.project_name}-lambda-statistics-dlq"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10"
  alarm_description   = "Alert when statistics DLQ has more than 10 messages"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.lambda_statistics_dlq.name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_statistics_errors" {
  alarm_name          = "${var.project_name}-lambda-statistics-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Alert when statistics Lambda has more than 5 errors in 10 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.statistics.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for Lambda duration (approaching timeout)
resource "aws_cloudwatch_metric_alarm" "lambda_statistics_duration" {
  alarm_name          = "${var.project_name}-lambda-statistics-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "50000" # 50 seconds (timeout is 60s)
  alarm_description   = "Alert when statistics Lambda duration approaches timeout"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.statistics.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for insufficient data points
resource "aws_cloudwatch_metric_alarm" "statistics_insufficient_data" {
  alarm_name          = "${var.project_name}-statistics-insufficient-data"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "3"
  metric_name         = "InsufficientDataPoints"
  namespace           = "KIA/PaintShop"
  period              = "300"
  statistic           = "Sum"
  threshold           = "20"
  alarm_description   = "Alert when many variables have insufficient data points"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# Output Lambda function ARN
output "lambda_statistics_arn" {
  description = "ARN of the statistics Lambda function"
  value       = aws_lambda_function.statistics.arn
}

output "lambda_statistics_name" {
  description = "Name of the statistics Lambda function"
  value       = aws_lambda_function.statistics.function_name
}

output "statistics_schedule_rule" {
  description = "EventBridge rule for statistics schedule"
  value       = aws_cloudwatch_event_rule.statistics_schedule.name
}
