# KIA Paint Shop IoT Prototype - API Lambda Functions Configuration

# Data source for packaging Lambda functions
data "archive_file" "lambda_api_list_variables" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/.terraform/lambda_packages/api_list_variables.zip"
  excludes    = ["__pycache__", "*.pyc", ".gitkeep", "README.md"]
}

data "archive_file" "lambda_api_get_variable_data" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/.terraform/lambda_packages/api_get_variable_data.zip"
  excludes    = ["__pycache__", "*.pyc", ".gitkeep", "README.md"]
}

data "archive_file" "lambda_api_list_alarms" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/.terraform/lambda_packages/api_list_alarms.zip"
  excludes    = ["__pycache__", "*.pyc", ".gitkeep", "README.md"]
}

data "archive_file" "lambda_api_acknowledge_alarm" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/.terraform/lambda_packages/api_acknowledge_alarm.zip"
  excludes    = ["__pycache__", "*.pyc", ".gitkeep", "README.md"]
}

data "archive_file" "lambda_api_get_statistics" {
  type        = "zip"
  source_dir  = "${path.module}/../lambdas/api"
  output_path = "${path.module}/.terraform/lambda_packages/api_get_statistics.zip"
  excludes    = ["__pycache__", "*.pyc", ".gitkeep", "README.md"]
}

# IAM Role for API Lambda Functions
resource "aws_iam_role" "lambda_api" {
  name = "${var.project_name}-lambda-api-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy for API Lambda Functions
resource "aws_iam_role_policy" "lambda_api" {
  name = "${var.project_name}-lambda-api-policy"
  role = aws_iam_role.lambda_api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${var.project_name}-api-*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:UpdateItem"
        ]
        Resource = [
          aws_dynamodb_table.sensor_data.arn,
          "${aws_dynamodb_table.sensor_data.arn}/index/*",
          aws_dynamodb_table.alarms.arn,
          "${aws_dynamodb_table.alarms.arn}/index/*",
          aws_dynamodb_table.statistics.arn,
          "${aws_dynamodb_table.statistics.arn}/index/*",
          aws_dynamodb_table.variables_metadata.arn,
          "${aws_dynamodb_table.variables_metadata.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.archive.arn,
          "${aws_s3_bucket.archive.arn}/*"
        ]
      },
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
      }
    ]
  })
}

# CloudWatch Log Groups for API Lambda Functions
resource "aws_cloudwatch_log_group" "lambda_api_list_variables" {
  name              = "/aws/lambda/${var.project_name}-api-list-variables"
  retention_in_days = var.cloudwatch_log_retention_days
}

resource "aws_cloudwatch_log_group" "lambda_api_get_variable_data" {
  name              = "/aws/lambda/${var.project_name}-api-get-variable-data"
  retention_in_days = var.cloudwatch_log_retention_days
}

resource "aws_cloudwatch_log_group" "lambda_api_list_alarms" {
  name              = "/aws/lambda/${var.project_name}-api-list-alarms"
  retention_in_days = var.cloudwatch_log_retention_days
}

resource "aws_cloudwatch_log_group" "lambda_api_acknowledge_alarm" {
  name              = "/aws/lambda/${var.project_name}-api-acknowledge-alarm"
  retention_in_days = var.cloudwatch_log_retention_days
}

resource "aws_cloudwatch_log_group" "lambda_api_get_statistics" {
  name              = "/aws/lambda/${var.project_name}-api-get-statistics"
  retention_in_days = var.cloudwatch_log_retention_days
}

# Lambda Function: list_variables
resource "aws_lambda_function" "api_list_variables" {
  filename         = data.archive_file.lambda_api_list_variables.output_path
  function_name    = "${var.project_name}-api-list-variables"
  role             = aws_iam_role.lambda_api.arn
  handler          = "list_variables.handler"
  source_code_hash = data.archive_file.lambda_api_list_variables.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = 256
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_VARIABLES_TABLE = aws_dynamodb_table.variables_metadata.name
      LOG_LEVEL                = "INFO"
      CLOUDWATCH_NAMESPACE     = "KIA/PaintShop"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_list_variables,
    aws_iam_role_policy.lambda_api
  ]
}

# Lambda Function: get_variable_data
resource "aws_lambda_function" "api_get_variable_data" {
  filename         = data.archive_file.lambda_api_get_variable_data.output_path
  function_name    = "${var.project_name}-api-get-variable-data"
  role             = aws_iam_role.lambda_api.arn
  handler          = "get_variable_data.handler"
  source_code_hash = data.archive_file.lambda_api_get_variable_data.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = 256
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_SENSOR_DATA_TABLE = aws_dynamodb_table.sensor_data.name
      S3_ARCHIVE_BUCKET          = aws_s3_bucket.archive.id
      LOG_LEVEL                  = "INFO"
      CLOUDWATCH_NAMESPACE       = "KIA/PaintShop"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_get_variable_data,
    aws_iam_role_policy.lambda_api
  ]
}

# Lambda Function: list_alarms
resource "aws_lambda_function" "api_list_alarms" {
  filename         = data.archive_file.lambda_api_list_alarms.output_path
  function_name    = "${var.project_name}-api-list-alarms"
  role             = aws_iam_role.lambda_api.arn
  handler          = "list_alarms.handler"
  source_code_hash = data.archive_file.lambda_api_list_alarms.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = 256
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_ALARMS_TABLE = aws_dynamodb_table.alarms.name
      LOG_LEVEL             = "INFO"
      CLOUDWATCH_NAMESPACE  = "KIA/PaintShop"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_list_alarms,
    aws_iam_role_policy.lambda_api
  ]
}

# Lambda Function: acknowledge_alarm
resource "aws_lambda_function" "api_acknowledge_alarm" {
  filename         = data.archive_file.lambda_api_acknowledge_alarm.output_path
  function_name    = "${var.project_name}-api-acknowledge-alarm"
  role             = aws_iam_role.lambda_api.arn
  handler          = "acknowledge_alarm.handler"
  source_code_hash = data.archive_file.lambda_api_acknowledge_alarm.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = 256
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_ALARMS_TABLE = aws_dynamodb_table.alarms.name
      LOG_LEVEL             = "INFO"
      CLOUDWATCH_NAMESPACE  = "KIA/PaintShop"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_acknowledge_alarm,
    aws_iam_role_policy.lambda_api
  ]
}

# Lambda Function: get_statistics
resource "aws_lambda_function" "api_get_statistics" {
  filename         = data.archive_file.lambda_api_get_statistics.output_path
  function_name    = "${var.project_name}-api-get-statistics"
  role             = aws_iam_role.lambda_api.arn
  handler          = "get_statistics.handler"
  source_code_hash = data.archive_file.lambda_api_get_statistics.output_base64sha256
  runtime          = var.lambda_runtime
  memory_size      = 256
  timeout          = 30

  environment {
    variables = {
      DYNAMODB_STATISTICS_TABLE = aws_dynamodb_table.statistics.name
      LOG_LEVEL                 = "INFO"
      CLOUDWATCH_NAMESPACE      = "KIA/PaintShop"
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.lambda_api_get_statistics,
    aws_iam_role_policy.lambda_api
  ]
}

# Outputs for API Lambda Functions
output "lambda_api_list_variables_arn" {
  description = "ARN of list_variables Lambda function"
  value       = aws_lambda_function.api_list_variables.arn
}

output "lambda_api_get_variable_data_arn" {
  description = "ARN of get_variable_data Lambda function"
  value       = aws_lambda_function.api_get_variable_data.arn
}

output "lambda_api_list_alarms_arn" {
  description = "ARN of list_alarms Lambda function"
  value       = aws_lambda_function.api_list_alarms.arn
}

output "lambda_api_acknowledge_alarm_arn" {
  description = "ARN of acknowledge_alarm Lambda function"
  value       = aws_lambda_function.api_acknowledge_alarm.arn
}

output "lambda_api_get_statistics_arn" {
  description = "ARN of get_statistics Lambda function"
  value       = aws_lambda_function.api_get_statistics.arn
}
