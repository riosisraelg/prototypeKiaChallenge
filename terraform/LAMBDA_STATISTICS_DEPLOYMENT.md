# Lambda Statistics Deployment Guide

## Overview

The statistics Lambda function requires numpy for efficient numerical calculations. Since numpy is not included in the standard Lambda Python runtime, it must be packaged with the function or provided as a Lambda Layer.

## Deployment Options

### Option 1: Package numpy with the function (Current Implementation)

This is the simplest approach for the prototype but increases deployment package size.

**Steps:**

1. Create a deployment package with dependencies:

```bash
cd lambdas/statistics

# Create a temporary directory for the package
mkdir -p package

# Install dependencies to the package directory
pip install -r requirements.txt -t package/

# Copy Lambda code to package
cp handler.py statistics_calculator.py package/

# Create deployment zip
cd package
zip -r ../lambda_statistics_deployment.zip .
cd ..

# Clean up
rm -rf package
```

2. Update Terraform to use the deployment package:

```hcl
# In lambda_statistics.tf, replace the data.archive_file with:
resource "aws_lambda_function" "statistics" {
  filename         = "${path.module}/../lambdas/statistics/lambda_statistics_deployment.zip"
  # ... rest of configuration
}
```

### Option 2: Use Lambda Layer (Recommended for Production)

Lambda Layers allow sharing dependencies across multiple functions and reduce deployment package size.

**Steps:**

1. Create numpy Lambda Layer:

```bash
# Create layer directory structure
mkdir -p lambda-layers/numpy/python

# Install numpy for Lambda runtime (Python 3.11, arm64)
pip install numpy==1.26.3 -t lambda-layers/numpy/python/

# Create layer zip
cd lambda-layers/numpy
zip -r numpy-layer.zip python/
cd ../..
```

2. Create Terraform resource for the layer:

```hcl
# Add to lambda_statistics.tf

resource "aws_lambda_layer_version" "numpy" {
  filename            = "${path.module}/../lambda-layers/numpy/numpy-layer.zip"
  layer_name          = "${var.project_name}-numpy"
  compatible_runtimes = ["python3.11"]
  compatible_architectures = ["arm64"]
  
  description = "NumPy 1.26.3 for statistics calculations"
}

# Update Lambda function to use the layer
resource "aws_lambda_function" "statistics" {
  # ... existing configuration
  
  layers = [aws_lambda_layer_version.numpy.arn]
}
```

### Option 3: Use AWS-Provided Layer (Simplest)

AWS provides pre-built layers for common scientific Python packages through AWS Lambda Powertools or third-party sources.

**Using AWS Data Wrangler (includes numpy, pandas):**

```hcl
# In lambda_statistics.tf
resource "aws_lambda_function" "statistics" {
  # ... existing configuration
  
  layers = [
    "arn:aws:lambda:${data.aws_region.current.name}:336392948345:layer:AWSSDKPandas-Python311-Arm64:1"
  ]
}
```

**Note:** Verify the layer ARN for your region at: https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html

## Current Implementation

The current Terraform configuration uses **Option 1** (package with function) for simplicity during prototype development. The `data.archive_file` resource packages the Lambda code but **does not include numpy**.

### To Deploy Successfully:

1. **Before running `terraform apply`**, create the deployment package with numpy:

```bash
cd lambdas/statistics
pip install -r requirements.txt -t .
```

This installs numpy directly in the `lambdas/statistics` directory, which will be included in the zip by Terraform.

2. **After deployment**, clean up if desired:

```bash
cd lambdas/statistics
rm -rf numpy* *.dist-info
```

### Alternative: Automated Deployment Script

Create `scripts/deploy_statistics_lambda.sh`:

```bash
#!/bin/bash
set -e

echo "Building statistics Lambda deployment package..."

cd lambdas/statistics

# Clean previous builds
rm -rf package lambda_statistics_deployment.zip

# Create package directory
mkdir package

# Install dependencies
pip install -r requirements.txt -t package/ --platform manylinux2014_aarch64 --only-binary=:all:

# Copy Lambda code
cp handler.py statistics_calculator.py package/

# Create zip
cd package
zip -r ../lambda_statistics_deployment.zip .
cd ..

# Clean up
rm -rf package

echo "Deployment package created: lambdas/statistics/lambda_statistics_deployment.zip"
echo "Size: $(du -h lambda_statistics_deployment.zip | cut -f1)"
```

Then update `lambda_statistics.tf`:

```hcl
resource "aws_lambda_function" "statistics" {
  filename         = "${path.module}/../lambdas/statistics/lambda_statistics_deployment.zip"
  function_name    = "${var.project_name}-statistics"
  # ... rest of configuration
  
  # Remove source_code_hash or update to use the deployment zip
  source_code_hash = filebase64sha256("${path.module}/../lambdas/statistics/lambda_statistics_deployment.zip")
}
```

## Deployment Checklist

- [ ] Choose deployment option (1, 2, or 3)
- [ ] Build deployment package with numpy
- [ ] Verify package size (should be < 50MB uncompressed)
- [ ] Test Lambda locally if possible
- [ ] Run `terraform plan` to verify configuration
- [ ] Run `terraform apply` to deploy
- [ ] Test Lambda function with EventBridge test event
- [ ] Monitor CloudWatch Logs for errors
- [ ] Verify statistics are being written to DynamoDB

## Troubleshooting

### Import Error: No module named 'numpy'

**Cause:** numpy not included in deployment package

**Solution:** Follow Option 1 steps to package numpy with the function

### Lambda timeout (60 seconds exceeded)

**Cause:** Processing too many variables or slow DynamoDB queries

**Solutions:**
- Increase Lambda timeout (max 15 minutes)
- Optimize DynamoDB queries
- Process variables in batches
- Consider parallel processing

### Package size too large (>50MB)

**Cause:** numpy compiled for wrong architecture or includes unnecessary files

**Solutions:**
- Use `--platform manylinux2014_aarch64` for arm64
- Use `--only-binary=:all:` to avoid source distributions
- Exclude test files and documentation
- Use Lambda Layer (Option 2)

### Statistics not appearing in DynamoDB

**Cause:** Insufficient data points or query errors

**Solutions:**
- Check CloudWatch Logs for errors
- Verify sensor data exists in time window
- Check `InsufficientDataPoints` metric
- Verify DynamoDB table permissions

## Cost Considerations

### Deployment Package Size Impact

- **Option 1 (package with function)**: ~20-30MB deployment package
  - Slower cold starts (~2-3 seconds)
  - Higher storage costs (minimal, ~$0.01/month)
  
- **Option 2 (Lambda Layer)**: ~5MB function + ~20MB layer
  - Faster cold starts (~1-2 seconds)
  - Layer can be shared across functions
  - Recommended for production

- **Option 3 (AWS-provided layer)**: ~5MB function + shared layer
  - Fastest cold starts (~1 second)
  - No layer management required
  - May include unnecessary dependencies

### Recommendation

For this prototype: **Option 1** (simplest)
For production: **Option 2 or 3** (better performance and maintainability)

## Testing

### Local Testing

```python
# test_statistics_local.py
import sys
sys.path.insert(0, 'lambdas/statistics')

from handler import handler

class MockContext:
    request_id = "test-123"

event = {
    "version": "0",
    "id": "test-event",
    "detail-type": "Scheduled Event",
    "source": "aws.events"
}

result = handler(event, MockContext())
print(result)
```

### Integration Testing

```bash
# Invoke Lambda directly
aws lambda invoke \
  --function-name kia-paintshop-prototype-statistics \
  --payload '{}' \
  response.json

cat response.json | jq .
```

## Monitoring

Key metrics to monitor:
- `StatisticsCalculated`: Should match number of active variables
- `InsufficientDataPoints`: Should be low (<10%)
- `ProcessingTimeMs`: Should be well below 60000ms
- Lambda Duration: Should be consistent
- Lambda Errors: Should be zero

## References

- [AWS Lambda Layers](https://docs.aws.amazon.com/lambda/latest/dg/configuration-layers.html)
- [AWS SDK for pandas Layers](https://aws-sdk-pandas.readthedocs.io/en/stable/layers.html)
- [NumPy on Lambda](https://github.com/numpy/numpy/wiki/Using-NumPy-on-AWS-Lambda)
