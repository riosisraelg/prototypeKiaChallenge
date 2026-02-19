# KIA Paint Shop IoT Prototype - DynamoDB Tables

# ============================================================================
# Table: sensor-data
# Purpose: Store real-time sensor data with 30-day TTL
# ============================================================================

resource "aws_dynamodb_table" "sensor_data" {
  name         = "${var.project_name}-sensor-data"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "area"
    type = "S"
  }

  attribute {
    name = "variable_id"
    type = "S"
  }

  attribute {
    name = "timestamp"
    type = "S"
  }

  # GSI1: Query by area and timestamp
  global_secondary_index {
    name            = "GSI1-area-timestamp"
    hash_key        = "area"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # GSI2: Query by variable_id and timestamp
  global_secondary_index {
    name            = "GSI2-variable-timestamp"
    hash_key        = "variable_id"
    range_key       = "timestamp"
    projection_type = "ALL"
  }

  # TTL configuration (30 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery for data protection
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-sensor-data"
    Description = "Sensor data with 30-day TTL"
  }
}

# ============================================================================
# Table: alarms
# Purpose: Store system alarms with status tracking
# ============================================================================

resource "aws_dynamodb_table" "alarms" {
  name         = "${var.project_name}-alarms"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "status"
    type = "S"
  }

  attribute {
    name = "created_at"
    type = "S"
  }

  attribute {
    name = "variable_id"
    type = "S"
  }

  # GSI1: Query by status and creation time
  global_secondary_index {
    name            = "GSI1-status-created"
    hash_key        = "status"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  # GSI2: Query by variable_id and creation time
  global_secondary_index {
    name            = "GSI2-variable-created"
    hash_key        = "variable_id"
    range_key       = "created_at"
    projection_type = "ALL"
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-alarms"
    Description = "System alarms with status tracking"
  }
}

# ============================================================================
# Table: statistics
# Purpose: Store aggregated statistics with 7-day TTL
# ============================================================================

resource "aws_dynamodb_table" "statistics" {
  name         = "${var.project_name}-statistics"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # TTL configuration (7 days)
  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-statistics"
    Description = "Aggregated statistics with 7-day TTL"
  }
}

# ============================================================================
# Table: variables-metadata
# Purpose: Store metadata for all 100 variables
# ============================================================================

resource "aws_dynamodb_table" "variables_metadata" {
  name         = "${var.project_name}-variables-metadata"
  billing_mode = var.dynamodb_billing_mode
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  attribute {
    name = "area"
    type = "S"
  }

  attribute {
    name = "variable_id"
    type = "S"
  }

  # GSI1: Query by area and variable_id
  global_secondary_index {
    name            = "GSI1-area-variable"
    hash_key        = "area"
    range_key       = "variable_id"
    projection_type = "ALL"
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # Server-side encryption
  server_side_encryption {
    enabled = true
  }

  tags = {
    Name        = "${var.project_name}-variables-metadata"
    Description = "Metadata for all system variables"
  }
}
