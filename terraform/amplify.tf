# KIA Paint Shop IoT Prototype - AWS Amplify Configuration
# Task 14.1: Dashboard deployment configuration

# Amplify App for React Dashboard
resource "aws_amplify_app" "dashboard" {
  name        = "${var.project_name}-dashboard-${var.environment}"
  description = "KIA Paint Shop IoT Prototype Dashboard - React + TypeScript"

  # Build settings for React app
  build_spec = <<-EOT
    version: 1
    frontend:
      phases:
        preBuild:
          commands:
            - npm ci
        build:
          commands:
            - npm run build
      artifacts:
        baseDirectory: build
        files:
          - '**/*'
      cache:
        paths:
          - node_modules/**/*
  EOT

  # Environment variables for React app
  environment_variables = {
    REACT_APP_API_URL = aws_api_gateway_stage.demo.invoke_url
    REACT_APP_API_KEY = aws_api_gateway_api_key.paintshop_api_key.value
    # Disable source maps in production for security
    GENERATE_SOURCEMAP = "false"
  }

  # Enable auto branch creation for Git-based deployments (optional)
  enable_auto_branch_creation = false
  enable_branch_auto_build    = false
  enable_branch_auto_deletion = false

  # Custom rules for SPA routing
  custom_rule {
    source = "/<*>"
    status = "404"
    target = "/index.html"
  }

  # Tags for resource management
  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Component   = "Dashboard"
  }
}

# Main branch for manual deployment
resource "aws_amplify_branch" "main" {
  app_id      = aws_amplify_app.dashboard.id
  branch_name = "main"

  # Environment variables can be overridden per branch if needed
  environment_variables = {
    REACT_APP_API_URL = aws_api_gateway_stage.demo.invoke_url
    REACT_APP_API_KEY = aws_api_gateway_api_key.paintshop_api_key.value
  }

  # Enable auto build if connected to Git repository
  enable_auto_build = false

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
  }
}

# Output Amplify app details
output "amplify_app_id" {
  description = "Amplify app ID"
  value       = aws_amplify_app.dashboard.id
}

output "amplify_app_arn" {
  description = "Amplify app ARN"
  value       = aws_amplify_app.dashboard.arn
}

output "amplify_default_domain" {
  description = "Amplify default domain"
  value       = aws_amplify_app.dashboard.default_domain
}

output "amplify_app_url" {
  description = "Amplify app URL (main branch)"
  value       = "https://main.${aws_amplify_app.dashboard.default_domain}"
}

# Note: For manual deployment, use the deploy script (scripts/deploy_dashboard.sh)
# For Git-based deployment, connect the Amplify app to your repository in AWS Console
