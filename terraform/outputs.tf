# KIA Paint Shop IoT Prototype - Terraform Outputs

output "aws_region" {
  description = "AWS region"
  value       = var.aws_region
}

output "aws_account_id" {
  description = "AWS account ID"
  value       = data.aws_caller_identity.current.account_id
}

# IoT Core outputs
output "iot_endpoint" {
  description = "AWS IoT Core endpoint"
  value       = data.aws_iot_endpoint.endpoint.endpoint_address
}

output "iot_thing_name" {
  description = "IoT Thing name"
  value       = aws_iot_thing.paintshop_simulator.name
}

output "iot_certificate_id" {
  description = "IoT certificate ID"
  value       = aws_iot_certificate.paintshop_cert.id
}

output "iot_certificate_arn" {
  description = "IoT certificate ARN"
  value       = aws_iot_certificate.paintshop_cert.arn
}

output "iot_topic_pattern" {
  description = "IoT MQTT topic pattern"
  value       = "kia/paintshop/+/+"
}

# DynamoDB outputs
output "dynamodb_sensor_data_table" {
  description = "DynamoDB sensor data table name"
  value       = aws_dynamodb_table.sensor_data.name
}

output "dynamodb_alarms_table" {
  description = "DynamoDB alarms table name"
  value       = aws_dynamodb_table.alarms.name
}

output "dynamodb_statistics_table" {
  description = "DynamoDB statistics table name"
  value       = aws_dynamodb_table.statistics.name
}

output "dynamodb_variables_metadata_table" {
  description = "DynamoDB variables metadata table name"
  value       = aws_dynamodb_table.variables_metadata.name
}

# S3 outputs
output "s3_archive_bucket" {
  description = "S3 archive bucket name"
  value       = aws_s3_bucket.archive.id
}

output "s3_archive_bucket_arn" {
  description = "S3 archive bucket ARN"
  value       = aws_s3_bucket.archive.arn
}

output "s3_archive_bucket_region" {
  description = "S3 archive bucket region"
  value       = aws_s3_bucket.archive.region
}

# API Gateway outputs
output "api_url" {
  description = "API Gateway invoke URL"
  value       = aws_api_gateway_stage.demo.invoke_url
}

output "api_key" {
  description = "API Gateway API key"
  value       = aws_api_gateway_api_key.paintshop_api_key.value
  sensitive   = true
}

# Lambda outputs
output "lambda_ingest_arn" {
  description = "Ingest Lambda function ARN"
  value       = aws_lambda_function.ingest.arn
}

output "lambda_ingest_name" {
  description = "Ingest Lambda function name"
  value       = aws_lambda_function.ingest.function_name
}

# Note: Process and Statistics Lambda outputs are defined in their respective .tf files
# - lambda_process.tf defines lambda_process_arn and lambda_process_name
# - lambda_statistics.tf defines lambda_statistics_arn and lambda_statistics_name

# EventBridge outputs
output "eventbridge_bus_name" {
  description = "EventBridge bus name"
  value       = aws_cloudwatch_event_bus.paintshop.name
}

output "eventbridge_bus_arn" {
  description = "EventBridge bus ARN"
  value       = aws_cloudwatch_event_bus.paintshop.arn
}

# DLQ outputs
output "lambda_ingest_dlq_url" {
  description = "Lambda ingest DLQ URL"
  value       = aws_sqs_queue.lambda_ingest_dlq.url
}

output "lambda_ingest_dlq_arn" {
  description = "Lambda ingest DLQ ARN"
  value       = aws_sqs_queue.lambda_ingest_dlq.arn
}

output "lambda_process_dlq_url" {
  description = "Lambda process DLQ URL"
  value       = aws_sqs_queue.lambda_process_dlq.url
}

output "lambda_process_dlq_arn" {
  description = "Lambda process DLQ ARN"
  value       = aws_sqs_queue.lambda_process_dlq.arn
}

output "lambda_statistics_dlq_url" {
  description = "Lambda statistics DLQ URL"
  value       = aws_sqs_queue.lambda_statistics_dlq.url
}

output "lambda_statistics_dlq_arn" {
  description = "Lambda statistics DLQ ARN"
  value       = aws_sqs_queue.lambda_statistics_dlq.arn
}

# CloudWatch outputs
output "cloudwatch_namespace" {
  description = "CloudWatch custom metrics namespace"
  value       = "KIA/PaintShop"
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alarm notifications"
  value       = try(aws_sns_topic.alarms.arn, "")
}

output "cloudwatch_dashboard_name" {
  description = "CloudWatch dashboard name"
  value       = try(aws_cloudwatch_dashboard.main.dashboard_name, "")
}

output "cloudwatch_log_groups" {
  description = "CloudWatch log groups for Lambda functions"
  value = {
    ingest                = try(aws_cloudwatch_log_group.lambda_ingest.name, "")
    process               = try(aws_cloudwatch_log_group.lambda_process.name, "")
    statistics            = try(aws_cloudwatch_log_group.lambda_statistics.name, "")
    api_list_variables    = try(aws_cloudwatch_log_group.lambda_api_list_variables.name, "")
    api_get_variable_data = try(aws_cloudwatch_log_group.lambda_api_get_variable_data.name, "")
    api_list_alarms       = try(aws_cloudwatch_log_group.lambda_api_list_alarms.name, "")
    api_acknowledge_alarm = try(aws_cloudwatch_log_group.lambda_api_acknowledge_alarm.name, "")
    api_get_statistics    = try(aws_cloudwatch_log_group.lambda_api_get_statistics.name, "")
  }
}
