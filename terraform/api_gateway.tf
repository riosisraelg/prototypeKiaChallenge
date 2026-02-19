# KIA Paint Shop IoT Prototype - API Gateway Configuration

# API Gateway REST API
resource "aws_api_gateway_rest_api" "paintshop_api" {
  name        = "${var.project_name}-api"
  description = "API REST para consultas de datos del Paint Shop"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  # Enforce minimum TLS version 1.2
  minimum_compression_size = -1 # Disable compression for security
}

# API Gateway Resources (endpoints)

# /variables
resource "aws_api_gateway_resource" "variables" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_rest_api.paintshop_api.root_resource_id
  path_part   = "variables"
}

# /variables/{id}
resource "aws_api_gateway_resource" "variables_id" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_resource.variables.id
  path_part   = "{id}"
}

# /variables/{id}/data
resource "aws_api_gateway_resource" "variables_id_data" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_resource.variables_id.id
  path_part   = "data"
}

# /alarms
resource "aws_api_gateway_resource" "alarms" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_rest_api.paintshop_api.root_resource_id
  path_part   = "alarms"
}

# /alarms/{id}
resource "aws_api_gateway_resource" "alarms_id" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_resource.alarms.id
  path_part   = "{id}"
}

# /alarms/{id}/acknowledge
resource "aws_api_gateway_resource" "alarms_id_acknowledge" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_resource.alarms_id.id
  path_part   = "acknowledge"
}

# /statistics
resource "aws_api_gateway_resource" "statistics" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_rest_api.paintshop_api.root_resource_id
  path_part   = "statistics"
}

# /statistics/{variable_id}
resource "aws_api_gateway_resource" "statistics_variable_id" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  parent_id   = aws_api_gateway_resource.statistics.id
  path_part   = "{variable_id}"
}

# CORS Configuration - OPTIONS methods for all resources

# OPTIONS /variables
resource "aws_api_gateway_method" "variables_options" {
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  resource_id   = aws_api_gateway_resource.variables.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "variables_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables.id
  http_method = aws_api_gateway_method.variables_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "variables_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables.id
  http_method = aws_api_gateway_method.variables_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "variables_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables.id
  http_method = aws_api_gateway_method.variables_options.http_method
  status_code = aws_api_gateway_method_response.variables_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-api-key'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# OPTIONS /variables/{id}/data
resource "aws_api_gateway_method" "variables_id_data_options" {
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  resource_id   = aws_api_gateway_resource.variables_id_data.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "variables_id_data_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables_id_data.id
  http_method = aws_api_gateway_method.variables_id_data_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "variables_id_data_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables_id_data.id
  http_method = aws_api_gateway_method.variables_id_data_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "variables_id_data_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables_id_data.id
  http_method = aws_api_gateway_method.variables_id_data_options.http_method
  status_code = aws_api_gateway_method_response.variables_id_data_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-api-key'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# OPTIONS /alarms
resource "aws_api_gateway_method" "alarms_options" {
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  resource_id   = aws_api_gateway_resource.alarms.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "alarms_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms.id
  http_method = aws_api_gateway_method.alarms_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "alarms_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms.id
  http_method = aws_api_gateway_method.alarms_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "alarms_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms.id
  http_method = aws_api_gateway_method.alarms_options.http_method
  status_code = aws_api_gateway_method_response.alarms_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-api-key'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# OPTIONS /alarms/{id}/acknowledge
resource "aws_api_gateway_method" "alarms_id_acknowledge_options" {
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  resource_id   = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "alarms_id_acknowledge_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method = aws_api_gateway_method.alarms_id_acknowledge_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "alarms_id_acknowledge_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method = aws_api_gateway_method.alarms_id_acknowledge_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "alarms_id_acknowledge_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method = aws_api_gateway_method.alarms_id_acknowledge_options.http_method
  status_code = aws_api_gateway_method_response.alarms_id_acknowledge_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-api-key'"
    "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# OPTIONS /statistics/{variable_id}
resource "aws_api_gateway_method" "statistics_variable_id_options" {
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  resource_id   = aws_api_gateway_resource.statistics_variable_id.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "statistics_variable_id_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.statistics_variable_id.id
  http_method = aws_api_gateway_method.statistics_variable_id_options.http_method
  type        = "MOCK"

  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_method_response" "statistics_variable_id_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.statistics_variable_id.id
  http_method = aws_api_gateway_method.statistics_variable_id_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }

  response_models = {
    "application/json" = "Empty"
  }
}

resource "aws_api_gateway_integration_response" "statistics_variable_id_options" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.statistics_variable_id.id
  http_method = aws_api_gateway_method.statistics_variable_id_options.http_method
  status_code = aws_api_gateway_method_response.statistics_variable_id_options.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token,x-api-key'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# API Methods and Lambda Integrations

# GET /variables
resource "aws_api_gateway_method" "list_variables" {
  rest_api_id      = aws_api_gateway_rest_api.paintshop_api.id
  resource_id      = aws_api_gateway_resource.variables.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "list_variables" {
  rest_api_id             = aws_api_gateway_rest_api.paintshop_api.id
  resource_id             = aws_api_gateway_resource.variables.id
  http_method             = aws_api_gateway_method.list_variables.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_list_variables.invoke_arn
}

resource "aws_api_gateway_method_response" "list_variables" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables.id
  http_method = aws_api_gateway_method.list_variables.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# GET /variables/{id}/data
resource "aws_api_gateway_method" "get_variable_data" {
  rest_api_id      = aws_api_gateway_rest_api.paintshop_api.id
  resource_id      = aws_api_gateway_resource.variables_id_data.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true

  request_parameters = {
    "method.request.path.id"           = true
    "method.request.querystring.start" = false
    "method.request.querystring.end"   = false
  }
}

resource "aws_api_gateway_integration" "get_variable_data" {
  rest_api_id             = aws_api_gateway_rest_api.paintshop_api.id
  resource_id             = aws_api_gateway_resource.variables_id_data.id
  http_method             = aws_api_gateway_method.get_variable_data.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_get_variable_data.invoke_arn
}

resource "aws_api_gateway_method_response" "get_variable_data" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.variables_id_data.id
  http_method = aws_api_gateway_method.get_variable_data.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# GET /alarms
resource "aws_api_gateway_method" "list_alarms" {
  rest_api_id      = aws_api_gateway_rest_api.paintshop_api.id
  resource_id      = aws_api_gateway_resource.alarms.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true

  request_parameters = {
    "method.request.querystring.status" = false
  }
}

resource "aws_api_gateway_integration" "list_alarms" {
  rest_api_id             = aws_api_gateway_rest_api.paintshop_api.id
  resource_id             = aws_api_gateway_resource.alarms.id
  http_method             = aws_api_gateway_method.list_alarms.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_list_alarms.invoke_arn
}

resource "aws_api_gateway_method_response" "list_alarms" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms.id
  http_method = aws_api_gateway_method.list_alarms.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# POST /alarms/{id}/acknowledge
resource "aws_api_gateway_method" "acknowledge_alarm" {
  rest_api_id      = aws_api_gateway_rest_api.paintshop_api.id
  resource_id      = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = true

  request_parameters = {
    "method.request.path.id" = true
  }
}

resource "aws_api_gateway_integration" "acknowledge_alarm" {
  rest_api_id             = aws_api_gateway_rest_api.paintshop_api.id
  resource_id             = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method             = aws_api_gateway_method.acknowledge_alarm.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_acknowledge_alarm.invoke_arn
}

resource "aws_api_gateway_method_response" "acknowledge_alarm" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.alarms_id_acknowledge.id
  http_method = aws_api_gateway_method.acknowledge_alarm.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# GET /statistics/{variable_id}
resource "aws_api_gateway_method" "get_statistics" {
  rest_api_id      = aws_api_gateway_rest_api.paintshop_api.id
  resource_id      = aws_api_gateway_resource.statistics_variable_id.id
  http_method      = "GET"
  authorization    = "NONE"
  api_key_required = true

  request_parameters = {
    "method.request.path.variable_id" = true
  }
}

resource "aws_api_gateway_integration" "get_statistics" {
  rest_api_id             = aws_api_gateway_rest_api.paintshop_api.id
  resource_id             = aws_api_gateway_resource.statistics_variable_id.id
  http_method             = aws_api_gateway_method.get_statistics.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_get_statistics.invoke_arn
}

resource "aws_api_gateway_method_response" "get_statistics" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  resource_id = aws_api_gateway_resource.statistics_variable_id.id
  http_method = aws_api_gateway_method.get_statistics.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
  }
}

# Lambda permissions for API Gateway to invoke functions
resource "aws_lambda_permission" "api_list_variables" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_list_variables.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paintshop_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_get_variable_data" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_variable_data.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paintshop_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_list_alarms" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_list_alarms.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paintshop_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_acknowledge_alarm" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_acknowledge_alarm.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paintshop_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_get_statistics" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_get_statistics.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.paintshop_api.execution_arn}/*/*"
}

# API Key and Usage Plan Configuration

# Generate a random API key value
resource "random_password" "api_key" {
  length  = 32
  special = false
}

# Create API Key
resource "aws_api_gateway_api_key" "paintshop_api_key" {
  name    = "${var.project_name}-api-key"
  enabled = true
  value   = random_password.api_key.result
}

# Create Usage Plan with limits
resource "aws_api_gateway_usage_plan" "paintshop_usage_plan" {
  name        = "${var.project_name}-usage-plan"
  description = "Usage plan for Paint Shop API with daily limits"

  api_stages {
    api_id = aws_api_gateway_rest_api.paintshop_api.id
    stage  = aws_api_gateway_stage.demo.stage_name
  }

  quota_settings {
    limit  = 1000
    period = "DAY"
  }

  throttle_settings {
    rate_limit  = var.api_throttle_rate_limit
    burst_limit = var.api_throttle_burst_limit
  }
}

# Associate API Key with Usage Plan
resource "aws_api_gateway_usage_plan_key" "paintshop_usage_plan_key" {
  key_id        = aws_api_gateway_api_key.paintshop_api_key.id
  key_type      = "API_KEY"
  usage_plan_id = aws_api_gateway_usage_plan.paintshop_usage_plan.id
}

# API Gateway Deployment and Stage

# Create deployment
resource "aws_api_gateway_deployment" "paintshop_deployment" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.variables.id,
      aws_api_gateway_resource.variables_id_data.id,
      aws_api_gateway_resource.alarms.id,
      aws_api_gateway_resource.alarms_id_acknowledge.id,
      aws_api_gateway_resource.statistics_variable_id.id,
      aws_api_gateway_method.list_variables.id,
      aws_api_gateway_method.get_variable_data.id,
      aws_api_gateway_method.list_alarms.id,
      aws_api_gateway_method.acknowledge_alarm.id,
      aws_api_gateway_method.get_statistics.id,
      aws_api_gateway_integration.list_variables.id,
      aws_api_gateway_integration.get_variable_data.id,
      aws_api_gateway_integration.list_alarms.id,
      aws_api_gateway_integration.acknowledge_alarm.id,
      aws_api_gateway_integration.get_statistics.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_method.list_variables,
    aws_api_gateway_method.get_variable_data,
    aws_api_gateway_method.list_alarms,
    aws_api_gateway_method.acknowledge_alarm,
    aws_api_gateway_method.get_statistics,
    aws_api_gateway_integration.list_variables,
    aws_api_gateway_integration.get_variable_data,
    aws_api_gateway_integration.list_alarms,
    aws_api_gateway_integration.acknowledge_alarm,
    aws_api_gateway_integration.get_statistics,
  ]
}

# Create stage "demo"
resource "aws_api_gateway_stage" "demo" {
  deployment_id = aws_api_gateway_deployment.paintshop_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.paintshop_api.id
  stage_name    = var.environment

  # Enable CloudWatch logging
  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      caller         = "$context.identity.caller"
      user           = "$context.identity.user"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      resourcePath   = "$context.resourcePath"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }

  # Enable X-Ray tracing
  xray_tracing_enabled = true

  variables = {
    version = "v1"
  }

  # Note: API Gateway Regional endpoints use TLS 1.2 by default
  # Custom domain names can enforce specific TLS versions via aws_api_gateway_domain_name
}

# CloudWatch Log Group for API Gateway
resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/${var.project_name}"
  retention_in_days = var.cloudwatch_log_retention_days
}

# Enable CloudWatch logging for API Gateway
resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.paintshop_api.id
  stage_name  = aws_api_gateway_stage.demo.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled        = true
    logging_level          = "INFO"
    data_trace_enabled     = true
    throttling_rate_limit  = var.api_throttle_rate_limit
    throttling_burst_limit = var.api_throttle_burst_limit
  }
}

# IAM role for API Gateway to write to CloudWatch
resource "aws_iam_role" "api_gateway_cloudwatch" {
  name = "${var.project_name}-api-gateway-cloudwatch-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "apigateway.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "api_gateway_cloudwatch" {
  role       = aws_iam_role.api_gateway_cloudwatch.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonAPIGatewayPushToCloudWatchLogs"
}

# Set API Gateway account settings
resource "aws_api_gateway_account" "main" {
  cloudwatch_role_arn = aws_iam_role.api_gateway_cloudwatch.arn
}
