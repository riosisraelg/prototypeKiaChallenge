# KIA Paint Shop IoT Prototype - Terraform Variables

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "kia-paintshop-prototype"
}

variable "project_tag" {
  description = "Project tag value for AWS resources"
  type        = string
  default     = "KIA-PaintShop-Prototype"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "demo"
}

variable "environment_tag" {
  description = "Environment tag value for AWS resources"
  type        = string
  default     = "Demo"
}

variable "dynamodb_billing_mode" {
  description = "DynamoDB billing mode (PROVISIONED or PAY_PER_REQUEST)"
  type        = string
  default     = "PAY_PER_REQUEST"
}

variable "lambda_runtime" {
  description = "Lambda runtime version"
  type        = string
  default     = "python3.11"
}

variable "sensor_data_ttl_days" {
  description = "TTL for sensor data in DynamoDB (days)"
  type        = number
  default     = 30
}

variable "statistics_ttl_days" {
  description = "TTL for statistics in DynamoDB (days)"
  type        = number
  default     = 7
}

variable "cloudwatch_log_retention_days" {
  description = "CloudWatch log retention period (days)"
  type        = number
  default     = 7
}

variable "s3_lifecycle_glacier_days" {
  description = "Days before transitioning to Glacier"
  type        = number
  default     = 60
}

variable "s3_lifecycle_expiration_days" {
  description = "Days before deleting archived data"
  type        = number
  default     = 90
}

variable "api_throttle_rate_limit" {
  description = "API Gateway throttle rate limit (requests per second)"
  type        = number
  default     = 100
}

variable "api_throttle_burst_limit" {
  description = "API Gateway throttle burst limit"
  type        = number
  default     = 200
}

variable "budget_limit_usd" {
  description = "Monthly budget limit in USD"
  type        = number
  default     = 50
}

variable "cost_alert_threshold_usd" {
  description = "Cost alert threshold in USD"
  type        = number
  default     = 20
}
