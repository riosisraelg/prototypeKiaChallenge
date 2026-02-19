# KIA Paint Shop IoT Prototype - Lambda Process Function Configuration

# SQS Dead Letter Queue for Lambda failures
resource "aws_sqs_queue" "lambda_process_dlq" {
  name                      = "${var.project_name}-process-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "${var.project_name}-process-dlq"
  }
}

# IAM Role for Lambda Process Function
resource "aws_iam_role" "lambda_process" {
  name = "${var.project_name}-lambda-process-role"

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

# IAM Policy for Lambda Process Function
resource "aws_iam_role_policy" "lambda_process" {
  name = "${var.project_name}-lambda-process-policy"
  role = aws_iam_role.lambda_process.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # DynamoDB read permissions for variables metadata
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query"
        ]
        Resource = aws_dynamodb_table.variables_metadata.arn
      },
      # DynamoDB write permissions for alarms table
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.alarms.arn
      },
      # CloudWatch Logs permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_process.arn}:*"
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
        Resource = aws_sqs_queue.lambda_process_dlq.arn
      }
    ]
  })
}

# CloudWatch Log Group for Lambda Process
resource "aws_cloudwatch_log_group" "lambda_process" {
  name              = "/aws/lambda/${var.project_name}-process"
  retention_in_days = var.cloudwatch_log_retention_days
}

# Data source to create Lambda deployment package
data "archive_file" "lambda_process" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/process"
  output_path = "${path.module}/.terraform/lambda_process.zip"

  excludes = [
    "__pycache__",
    "*.pyc",
    ".gitkeep",
    "README.md"
  ]
}

# Lambda Function
resource "aws_lambda_function" "process" {
  filename         = data.archive_file.lambda_process.output_path
  function_name    = "${var.project_name}-process"
  role             = aws_iam_role.lambda_process.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.lambda_process.output_base64sha256

  runtime     = var.lambda_runtime
  memory_size = 512
  timeout     = 60

  environment {
    variables = {
      ALARMS_TABLE             = aws_dynamodb_table.alarms.name
      VARIABLES_METADATA_TABLE = aws_dynamodb_table.variables_metadata.name
      LOG_LEVEL                = "INFO"
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_process_dlq.arn
  }

  depends_on = [
    aws_iam_role_policy.lambda_process,
    aws_cloudwatch_log_group.lambda_process
  ]
}

# EventBridge Rule to trigger Lambda from sensor data events
resource "aws_cloudwatch_event_rule" "process_sensor_data" {
  name           = "${var.project_name}-process-sensor-data"
  description    = "Trigger process Lambda for sensor data anomaly detection"
  event_bus_name = aws_cloudwatch_event_bus.paintshop.name

  event_pattern = jsonencode({
    source      = ["kia.paintshop.ingest"]
    detail-type = ["Sensor Data Received"]
  })

  tags = {
    Name = "${var.project_name}-process-sensor-data"
  }
}

# EventBridge Target - Lambda Process Function
resource "aws_cloudwatch_event_target" "process_lambda" {
  rule           = aws_cloudwatch_event_rule.process_sensor_data.name
  event_bus_name = aws_cloudwatch_event_bus.paintshop.name
  target_id      = "ProcessLambda"
  arn            = aws_lambda_function.process.arn
}

# Lambda permission for EventBridge to invoke the function
resource "aws_lambda_permission" "allow_eventbridge_process" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.process.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.process_sensor_data.arn
}

# CloudWatch Alarm for DLQ messages
resource "aws_cloudwatch_metric_alarm" "lambda_process_dlq" {
  alarm_name          = "${var.project_name}-lambda-process-dlq"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10"
  alarm_description   = "Alert when process DLQ has more than 10 messages"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.lambda_process_dlq.name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for Lambda errors
resource "aws_cloudwatch_metric_alarm" "lambda_process_errors" {
  alarm_name          = "${var.project_name}-lambda-process-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Sum"
  threshold           = "5"
  alarm_description   = "Alert when process Lambda has more than 5 errors in 10 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.process.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for Lambda duration (approaching timeout)
resource "aws_cloudwatch_metric_alarm" "lambda_process_duration" {
  alarm_name          = "${var.project_name}-lambda-process-duration"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "Duration"
  namespace           = "AWS/Lambda"
  period              = "300"
  statistic           = "Maximum"
  threshold           = "50000" # 50 seconds (timeout is 60s)
  alarm_description   = "Alert when process Lambda duration approaches timeout"
  treat_missing_data  = "notBreaching"

  dimensions = {
    FunctionName = aws_lambda_function.process.function_name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# CloudWatch Alarm for high alarm generation rate
resource "aws_cloudwatch_metric_alarm" "high_alarm_rate" {
  alarm_name          = "${var.project_name}-high-alarm-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "AlarmsGenerated"
  namespace           = "KIA/PaintShop"
  period              = "300"
  statistic           = "Sum"
  threshold           = "50"
  alarm_description   = "Alert when alarm generation rate is unusually high (>50 in 10 minutes)"
  treat_missing_data  = "notBreaching"

  alarm_actions = [aws_sns_topic.alarms.arn]
}

# Output Lambda function ARN
output "lambda_process_arn" {
  description = "ARN of the process Lambda function"
  value       = aws_lambda_function.process.arn
}

output "lambda_process_name" {
  description = "Name of the process Lambda function"
  value       = aws_lambda_function.process.function_name
}

output "process_event_rule" {
  description = "EventBridge rule for process Lambda trigger"
  value       = aws_cloudwatch_event_rule.process_sensor_data.name
}
