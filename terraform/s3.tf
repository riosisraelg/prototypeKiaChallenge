# KIA Paint Shop IoT Prototype - S3 Archive Bucket Configuration

# S3 bucket for historical data archiving
resource "aws_s3_bucket" "archive" {
  bucket = "${var.project_name}-archive-${data.aws_caller_identity.current.account_id}"

  tags = {
    Name        = "${var.project_name}-archive"
    Description = "Historical data archive for IoT sensor data"
  }
}

# Enable versioning (optional but recommended for data protection)
resource "aws_s3_bucket_versioning" "archive" {
  bucket = aws_s3_bucket.archive.id

  versioning_configuration {
    status = "Disabled" # Disabled to minimize costs for prototype
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "archive" {
  bucket = aws_s3_bucket.archive.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable server-side encryption at rest
resource "aws_s3_bucket_server_side_encryption_configuration" "archive" {
  bucket = aws_s3_bucket.archive.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # Using AWS managed keys to avoid KMS costs
    }
    bucket_key_enabled = true
  }
}

# Configure lifecycle policies
resource "aws_s3_bucket_lifecycle_configuration" "archive" {
  bucket = aws_s3_bucket.archive.id

  # Rule for raw sensor data
  rule {
    id     = "archive-sensor-data"
    status = "Enabled"

    filter {
      prefix = "raw-data/"
    }

    # Transition to Glacier after 60 days
    transition {
      days          = var.s3_lifecycle_glacier_days
      storage_class = "GLACIER"
    }

    # Delete after 90 days
    expiration {
      days = var.s3_lifecycle_expiration_days
    }

    # Clean up incomplete multipart uploads
    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Rule for alarms data
  rule {
    id     = "archive-alarms"
    status = "Enabled"

    filter {
      prefix = "alarms/"
    }

    # Transition to Glacier after 60 days
    transition {
      days          = var.s3_lifecycle_glacier_days
      storage_class = "GLACIER"
    }

    # Delete after 90 days
    expiration {
      days = var.s3_lifecycle_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }

  # Rule for statistics data
  rule {
    id     = "archive-statistics"
    status = "Enabled"

    filter {
      prefix = "statistics/"
    }

    # Transition to Glacier after 60 days
    transition {
      days          = var.s3_lifecycle_glacier_days
      storage_class = "GLACIER"
    }

    # Delete after 90 days
    expiration {
      days = var.s3_lifecycle_expiration_days
    }

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}

# Create folder structure using null resources (for documentation purposes)
# Note: S3 doesn't have real folders, but we document the expected structure here
# The actual structure will be created when data is uploaded with proper prefixes

# Expected S3 structure:
# s3://kia-paintshop-prototype-archive-{account-id}/
# ├── raw-data/
# │   ├── year=2024/
# │   │   ├── month=01/
# │   │   │   ├── day=15/
# │   │   │   │   ├── area=pre-treatment/
# │   │   │   │   │   └── data.parquet.gz
# │   │   │   │   ├── area=e-coat/
# │   │   │   │   │   └── data.parquet.gz
# │   │   │   │   └── area=production-control/
# │   │   │   │       └── data.parquet.gz
# ├── alarms/
# │   └── year=2024/
# │       └── month=01/
# │           └── alarms.json.gz
# └── statistics/
#     └── year=2024/
#         └── month=01/
#             └── stats.parquet.gz
