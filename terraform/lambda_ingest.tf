# KIA Paint Shop IoT Prototype - Lambda Ingest Function Configuration

# EventBridge Event Bus for Lambda communication
resource "aws_cloudwatch_event_bus" "paintshop" {
  name = "${var.project_name}-event-bus"
}

# SQS Dead Letter Queue for Lambda failures
resource "aws_sqs_queue" "lambda_ingest_dlq" {
  name                      = "${var.project_name}-ingest-dlq"
  message_retention_seconds = 1209600 # 14 days

  tags = {
    Name = "${var.project_name}-ingest-dlq"
  }
}

# IAM Role for Lambda Ingest Function
resource "aws_iam_role" "lambda_ingest" {
  name = "${var.project_name}-lambda-ingest-role"

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

# IAM Policy for Lambda Ingest Function
resource "aws_iam_role_policy" "lambda_ingest" {
  name = "${var.project_name}-lambda-ingest-policy"
  role = aws_iam_role.lambda_ingest.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # DynamoDB write permissions
      {
        Effect = "Allow"
        Action = [
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.sensor_data.arn
      },
      # EventBridge put events permissions
      {
        Effect = "Allow"
        Action = [
          "events:PutEvents"
        ]
        Resource = aws_cloudwatch_event_bus.paintshop.arn
      },
      # CloudWatch Logs permissions
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.lambda_ingest.arn}:*"
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
        Resource = aws_sqs_queue.lambda_ingest_dlq.arn
      }
    ]
  })
}

# Data source to create Lambda deployment package
data "archive_file" "lambda_ingest" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/ingest"
  output_path = "${path.module}/.terraform/lambda_ingest.zip"

  excludes = [
    "__pycache__",
    "*.pyc",
    ".gitkeep",
    "README.md",
    "requirements.txt"
  ]
}

# Lambda Function
resource "aws_lambda_function" "ingest" {
  filename         = data.archive_file.lambda_ingest.output_path
  function_name    = "${var.project_name}-ingest"
  role             = aws_iam_role.lambda_ingest.arn
  handler          = "handler.handler"
  source_code_hash = data.archive_file.lambda_ingest.output_base64sha256

  runtime     = var.lambda_runtime
  memory_size = 256
  timeout     = 30

  environment {
    variables = {
      DYNAMODB_TABLE  = aws_dynamodb_table.sensor_data.name
      EVENTBRIDGE_BUS = aws_cloudwatch_event_bus.paintshop.name
      LOG_LEVEL       = "INFO"
      TTL_DAYS        = var.sensor_data_ttl_days
    }
  }

  dead_letter_config {
    target_arn = aws_sqs_queue.lambda_ingest_dlq.arn
  }

  depends_on = [
    aws_iam_role_policy.lambda_ingest
  ]
}

# Lambda permission for IoT Core to invoke the function
resource "aws_lambda_permission" "allow_iot" {
  statement_id  = "AllowExecutionFromIoT"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ingest.function_name
  principal     = "iot.amazonaws.com"
  source_arn    = aws_iot_topic_rule.paintshop_rule.arn
}

# CloudWatch Alarm for DLQ messages
resource "aws_cloudwatch_metric_alarm" "lambda_ingest_dlq" {
  alarm_name          = "${var.project_name}-lambda-ingest-dlq"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "300"
  statistic           = "Average"
  threshold           = "10"
  alarm_description   = "Alert when DLQ has more than 10 messages"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.lambda_ingest_dlq.name
  }

  alarm_actions = [aws_sns_topic.alarms.arn]
}
