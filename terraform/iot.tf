# KIA Paint Shop IoT Prototype - AWS IoT Core Configuration

# IoT Thing for the simulator
resource "aws_iot_thing" "paintshop_simulator" {
  name = "${var.project_name}-simulator"
}

# IoT Policy with minimum privileges
resource "aws_iot_policy" "paintshop_policy" {
  name = "${var.project_name}-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "iot:Connect"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:client/${var.project_name}-*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Publish"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/kia/paintshop/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Subscribe"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topicfilter/kia/paintshop/commands/*"
      },
      {
        Effect = "Allow"
        Action = [
          "iot:Receive"
        ]
        Resource = "arn:aws:iot:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:topic/kia/paintshop/commands/*"
      }
    ]
  })
}

# X.509 Certificate for authentication
resource "aws_iot_certificate" "paintshop_cert" {
  active = true
}

# Attach policy to certificate
resource "aws_iot_policy_attachment" "paintshop_policy_attachment" {
  policy = aws_iot_policy.paintshop_policy.name
  target = aws_iot_certificate.paintshop_cert.arn
}

# Attach certificate to thing
resource "aws_iot_thing_principal_attachment" "paintshop_thing_attachment" {
  thing     = aws_iot_thing.paintshop_simulator.name
  principal = aws_iot_certificate.paintshop_cert.arn
}

# IAM role for IoT Rule to invoke Lambda
resource "aws_iam_role" "iot_rule_role" {
  name = "${var.project_name}-iot-rule-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "iot.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# IAM policy for IoT Rule to invoke Lambda (placeholder - will be updated when Lambda is created)
resource "aws_iam_role_policy" "iot_rule_policy" {
  name = "${var.project_name}-iot-rule-policy"
  role = aws_iam_role.iot_rule_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "lambda:InvokeFunction"
        ]
        Resource = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-ingest"
      }
    ]
  })
}

# IoT Rule to route messages to Lambda
resource "aws_iot_topic_rule" "paintshop_rule" {
  name        = replace("${var.project_name}_ingest_rule", "-", "_")
  description = "Route paint shop sensor data to ingest Lambda"
  enabled     = true
  sql         = "SELECT topic(3) as area, topic(4) as variable_id, * FROM 'kia/paintshop/+/+' WHERE timestamp IS NOT NULL"
  sql_version = "2016-03-23"

  lambda {
    function_arn = "arn:aws:lambda:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:function:${var.project_name}-ingest"
  }

  error_action {
    cloudwatch_logs {
      log_group_name = aws_cloudwatch_log_group.iot_rule_errors.name
      role_arn       = aws_iam_role.iot_rule_role.arn
    }
  }
}

# CloudWatch Log Group for IoT Rule errors
resource "aws_cloudwatch_log_group" "iot_rule_errors" {
  name              = "/aws/iot/rules/${var.project_name}"
  retention_in_days = var.cloudwatch_log_retention_days
}

# IAM policy for IoT Rule to write to CloudWatch Logs
resource "aws_iam_role_policy" "iot_rule_cloudwatch_policy" {
  name = "${var.project_name}-iot-rule-cloudwatch-policy"
  role = aws_iam_role.iot_rule_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "${aws_cloudwatch_log_group.iot_rule_errors.arn}:*"
      }
    ]
  })
}

# Data source to get IoT endpoint
data "aws_iot_endpoint" "endpoint" {
  endpoint_type = "iot:Data-ATS"
}

# Local file to save certificate and private key for simulator
resource "local_file" "device_certificate" {
  content  = aws_iot_certificate.paintshop_cert.certificate_pem
  filename = "${path.module}/../simulator/certs/device.crt"
}

resource "local_file" "device_private_key" {
  content         = aws_iot_certificate.paintshop_cert.private_key
  filename        = "${path.module}/../simulator/certs/device.key"
  file_permission = "0600"
}

resource "local_file" "device_public_key" {
  content  = aws_iot_certificate.paintshop_cert.public_key
  filename = "${path.module}/../simulator/certs/device.pub"
}

# Note: Outputs are defined in outputs.tf to avoid duplication

