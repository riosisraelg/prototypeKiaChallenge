# Troubleshooting Guide

Common issues and solutions for the KIA Paint Shop IoT Prototype.

## Table of Contents

1. [Deployment Issues](#deployment-issues)
2. [Simulator Issues](#simulator-issues)
3. [Lambda Issues](#lambda-issues)
4. [API Issues](#api-issues)
5. [Dashboard Issues](#dashboard-issues)
6. [Data Flow Issues](#data-flow-issues)
7. [Cost Issues](#cost-issues)
8. [Cleanup Issues](#cleanup-issues)

---

## Deployment Issues

### Terraform init fails

**Symptom:**
```
Error: Failed to install provider
```

**Causes & Solutions:**

1. **No internet connection**
   ```bash
   # Test connectivity
   ping terraform.io
   ```

2. **Terraform version too old**
   ```bash
   # Check version
   terraform version
   
   # Upgrade to >= 1.5.0
   brew upgrade terraform  # macOS
   ```

3. **AWS credentials not configured**
   ```bash
   # Configure AWS CLI
   aws configure
   
   # Test credentials
   aws sts get-caller-identity
   ```

---

### Terraform apply fails

**Symptom:**
```
Error: Error creating Lambda function
```

**Common Causes:**

1. **Insufficient IAM permissions**
   ```bash
   # Check your IAM permissions
   aws iam get-user
   
   # Required permissions:
   # - Lambda: CreateFunction, UpdateFunction
   # - IAM: CreateRole, AttachRolePolicy
   # - DynamoDB: CreateTable
   # - IoT: CreateThing, CreateCertificate
   # - S3: CreateBucket
   # - API Gateway: CreateRestApi
   ```

2. **Resource name conflicts**
   ```bash
   # Change project name in variables.tf
   variable "project_name" {
     default = "kia-paintshop-unique-name"
   }
   ```

3. **Region not supported**
   ```bash
   # Use supported region
   export AWS_REGION=us-east-1
   ```

4. **Lambda deployment package too large**
   ```bash
   # Check package size
   du -sh lambdas/*/
   
   # Remove unnecessary files
   find lambdas -name "__pycache__" -exec rm -rf {} +
   find lambdas -name "*.pyc" -delete
   ```

---

### IoT certificates not created

**Symptom:**
```
Error: Certificate not found
```

**Solution:**
```bash
# Create certificate manually
aws iot create-keys-and-certificate \
  --set-as-active \
  --certificate-pem-outfile simulator/certs/certificate.pem \
  --public-key-outfile simulator/certs/public.key \
  --private-key-outfile simulator/certs/private.key

# Download root CA
curl https://www.amazontrust.com/repository/AmazonRootCA1.pem \
  -o simulator/certs/root-CA.crt

# Attach policy to certificate
aws iot attach-policy \
  --policy-name kia-paintshop-iot-policy \
  --target CERTIFICATE_ARN
```

---

## Simulator Issues

### Simulator won't start

**Symptom:**
```
ModuleNotFoundError: No module named 'paho'
```

**Solution:**
```bash
# Install dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

---

### MQTT connection fails

**Symptom:**
```
Error: Connection refused
Error: SSL handshake failed
```

**Causes & Solutions:**

1. **Missing certificates**
   ```bash
   # Check certificates exist
   ls -la simulator/certs/
   
   # Should have:
   # - certificate.pem
   # - private.key
   # - root-CA.crt
   ```

2. **Wrong IoT endpoint**
   ```bash
   # Get correct endpoint
   cd terraform
   terraform output iot_endpoint
   
   # Update config.yaml
   mqtt:
     host: "YOUR-ENDPOINT.iot.us-east-1.amazonaws.com"
   ```

3. **Certificate not attached to policy**
   ```bash
   # List certificates
   aws iot list-certificates
   
   # Attach policy
   aws iot attach-policy \
     --policy-name kia-paintshop-iot-policy \
     --target CERTIFICATE_ARN
   ```

4. **Firewall blocking port 8883**
   ```bash
   # Test connectivity
   telnet YOUR-ENDPOINT.iot.us-east-1.amazonaws.com 8883
   
   # Or use openssl
   openssl s_client -connect YOUR-ENDPOINT.iot.us-east-1.amazonaws.com:8883
   ```

---

### No data being published

**Symptom:**
Simulator runs but no data appears in DynamoDB

**Debugging Steps:**

1. **Check simulator logs**
   ```bash
   # Run with verbose logging
   python simulator/simulator.py --log-level DEBUG
   ```

2. **Verify MQTT messages**
   ```bash
   # Subscribe to IoT Core topic
   aws iot-data subscribe \
     --topic "kia/paintshop/#" \
     --region us-east-1
   ```

3. **Check IoT Core metrics**
   ```bash
   # View message count in CloudWatch
   aws cloudwatch get-metric-statistics \
     --namespace AWS/IoT \
     --metric-name PublishIn.Success \
     --start-time 2026-02-19T00:00:00Z \
     --end-time 2026-02-19T23:59:59Z \
     --period 3600 \
     --statistics Sum
   ```

4. **Verify IoT Rule is active**
   ```bash
   # List IoT Rules
   aws iot list-topic-rules
   
   # Get rule details
   aws iot get-topic-rule --rule-name kia_paintshop_ingest_rule
   ```

---

### CSV file not found

**Symptom:**
```
FileNotFoundError: KMX-PA-PT-F-001.csv
```

**Solution:**
```bash
# Check files exist
ls -la *.csv

# Run from correct directory
cd /path/to/project
python simulator/simulator.py
```

---

## Lambda Issues

### Lambda function not triggered

**Symptom:**
No Lambda invocations in CloudWatch

**Debugging Steps:**

1. **Check IoT Rule**
   ```bash
   # Verify rule is enabled
   aws iot get-topic-rule --rule-name kia_paintshop_ingest_rule
   ```

2. **Check Lambda permissions**
   ```bash
   # Verify IoT can invoke Lambda
   aws lambda get-policy \
     --function-name kia-paintshop-ingest
   ```

3. **Test Lambda manually**
   ```bash
   # Invoke Lambda with test event
   aws lambda invoke \
     --function-name kia-paintshop-ingest \
     --payload file://test-event.json \
     response.json
   ```

---

### Lambda timeout errors

**Symptom:**
```
Task timed out after 30.00 seconds
```

**Solutions:**

1. **Increase timeout**
   ```hcl
   # In terraform/lambda_*.tf
   resource "aws_lambda_function" "ingest" {
     timeout = 60  # Increase from 30
   }
   ```

2. **Optimize code**
   ```python
   # Use batch operations
   dynamodb.batch_write_item(...)
   
   # Reduce external API calls
   # Cache frequently accessed data
   ```

3. **Increase memory**
   ```hcl
   resource "aws_lambda_function" "ingest" {
     memory_size = 512  # Increase from 256
   }
   ```

---

### Lambda out of memory

**Symptom:**
```
Runtime exited with error: signal: killed
Runtime.ExitError
```

**Solution:**
```hcl
# Increase memory allocation
resource "aws_lambda_function" "statistics" {
  memory_size = 1024  # Increase from 512
}
```

---

### DynamoDB write errors

**Symptom:**
```
ProvisionedThroughputExceededException
```

**Solution:**
```python
# DynamoDB is on-demand, this shouldn't happen
# Check for:
# 1. Burst traffic (>4000 WCU/sec)
# 2. Hot partition keys
# 3. Large item sizes

# Add exponential backoff
import time
from botocore.exceptions import ClientError

def write_with_retry(item, max_retries=3):
    for attempt in range(max_retries):
        try:
            table.put_item(Item=item)
            return
        except ClientError as e:
            if e.response['Error']['Code'] == 'ProvisionedThroughputExceededException':
                time.sleep(2 ** attempt)
            else:
                raise
```

---

## API Issues

### 401 Unauthorized

**Symptom:**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Missing or invalid API key"
  }
}
```

**Solutions:**

1. **Get correct API key**
   ```bash
   cd terraform
   terraform output api_key
   ```

2. **Use correct header**
   ```bash
   curl -H "x-api-key: YOUR_API_KEY" \
     https://your-api-url.amazonaws.com/demo/variables
   ```

3. **Check API key is associated with usage plan**
   ```bash
   aws apigateway get-usage-plans
   ```

---

### 404 Not Found

**Symptom:**
```
{"message":"Missing Authentication Token"}
```

**Causes:**

1. **Wrong URL**
   ```bash
   # Get correct URL
   cd terraform
   terraform output api_url
   
   # Should be:
   # https://xxxxx.execute-api.us-east-1.amazonaws.com/demo
   ```

2. **Missing stage name**
   ```bash
   # Wrong: https://xxxxx.execute-api.us-east-1.amazonaws.com/variables
   # Right: https://xxxxx.execute-api.us-east-1.amazonaws.com/demo/variables
   ```

3. **Endpoint doesn't exist**
   ```bash
   # Check available endpoints
   aws apigateway get-resources \
     --rest-api-id YOUR_API_ID
   ```

---

### 429 Too Many Requests

**Symptom:**
```json
{
  "message": "Limit Exceeded"
}
```

**Solution:**
```bash
# Check usage plan limits
aws apigateway get-usage-plans

# Current limits:
# - 1000 requests/day
# - 100 requests/second

# Reduce request frequency
# Implement exponential backoff
# Use client-side caching
```

---

### CORS errors in browser

**Symptom:**
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```

**Solution:**
```bash
# Verify CORS is enabled in API Gateway
aws apigateway get-method \
  --rest-api-id YOUR_API_ID \
  --resource-id YOUR_RESOURCE_ID \
  --http-method OPTIONS

# Should return CORS headers:
# Access-Control-Allow-Origin: *
# Access-Control-Allow-Methods: GET,POST,OPTIONS
# Access-Control-Allow-Headers: Content-Type,x-api-key
```

---

## Dashboard Issues

### Dashboard won't start

**Symptom:**
```
npm ERR! missing script: start
```

**Solution:**
```bash
cd dashboard

# Install dependencies
npm install

# Start development server
npm start
```

---

### API connection fails

**Symptom:**
```
Network Error
Failed to fetch
```

**Solutions:**

1. **Check API URL in .env**
   ```bash
   # Create .env file
   cat > .env << EOF
   REACT_APP_API_URL=https://your-api-url.amazonaws.com/demo
   REACT_APP_API_KEY=your-api-key-here
   EOF
   
   # Restart development server
   npm start
   ```

2. **Verify API is deployed**
   ```bash
   curl -H "x-api-key: YOUR_KEY" \
     https://your-api-url.amazonaws.com/demo/variables
   ```

3. **Check browser console for errors**
   - Open DevTools (F12)
   - Check Console tab
   - Check Network tab

---

### No data displayed

**Symptom:**
Dashboard loads but shows no variables/data

**Debugging:**

1. **Check API response**
   ```javascript
   // In browser console
   fetch('https://your-api-url.amazonaws.com/demo/variables', {
     headers: { 'x-api-key': 'YOUR_KEY' }
   })
   .then(r => r.json())
   .then(console.log)
   ```

2. **Check simulator is running**
   ```bash
   ps aux | grep simulator.py
   ```

3. **Check DynamoDB has data**
   ```bash
   aws dynamodb scan \
     --table-name kia-paintshop-sensor-data \
     --limit 10
   ```

---

### Build fails

**Symptom:**
```
npm ERR! Failed to compile
```

**Solutions:**

1. **TypeScript errors**
   ```bash
   # Check for type errors
   npm run build
   
   # Fix type errors in code
   # Or add // @ts-ignore if needed
   ```

2. **Missing dependencies**
   ```bash
   # Reinstall dependencies
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Node version mismatch**
   ```bash
   # Check Node version
   node --version
   
   # Should be >= 16.x
   # Upgrade if needed
   ```

---

## Data Flow Issues

### Data not reaching DynamoDB

**Symptom:**
Simulator publishes but DynamoDB table is empty

**Debugging Steps:**

1. **Check IoT Core metrics**
   ```bash
   # CloudWatch > Metrics > AWS/IoT
   # Check: PublishIn.Success
   ```

2. **Check Lambda ingest logs**
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-ingest --follow
   ```

3. **Check IoT Rule errors**
   ```bash
   # CloudWatch > Metrics > AWS/IoT
   # Check: RuleMessageThrottled, RuleNotFound
   ```

4. **Test end-to-end**
   ```bash
   # 1. Publish test message
   aws iot-data publish \
     --topic "kia/paintshop/pre-treatment/TEST_VAR" \
     --payload '{"variable_id":"TEST_VAR","value":42}'
   
   # 2. Check Lambda was invoked
   aws logs tail /aws/lambda/kia-paintshop-ingest
   
   # 3. Check DynamoDB
   aws dynamodb get-item \
     --table-name kia-paintshop-sensor-data \
     --key '{"variable_id":{"S":"TEST_VAR"},"timestamp":{"S":"2026-02-19T12:00:00Z"}}'
   ```

---

### Alarms not generating

**Symptom:**
Values exceed thresholds but no alarms in DynamoDB

**Debugging:**

1. **Check EventBridge rule**
   ```bash
   aws events list-rules
   aws events list-targets-by-rule --rule kia-paintshop-process-trigger
   ```

2. **Check Lambda process logs**
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-process --follow
   ```

3. **Verify alarm logic**
   ```python
   # In lambdas/process/anomaly_detector.py
   # Check threshold comparison logic
   ```

---

### Statistics not calculating

**Symptom:**
No statistics in DynamoDB statistics table

**Debugging:**

1. **Check EventBridge scheduled rule**
   ```bash
   aws events describe-rule --name kia-paintshop-statistics-schedule
   ```

2. **Check Lambda statistics logs**
   ```bash
   aws logs tail /aws/lambda/kia-paintshop-statistics --follow
   ```

3. **Verify sufficient data**
   ```bash
   # Statistics require minimum 3 data points
   aws dynamodb query \
     --table-name kia-paintshop-sensor-data \
     --key-condition-expression "variable_id = :vid" \
     --expression-attribute-values '{":vid":{"S":"PT_TEMP_TANK_1"}}'
   ```

---

## Cost Issues

### Unexpected high costs

**Symptom:**
AWS bill higher than expected

**Investigation:**

1. **Run cost check**
   ```bash
   ./scripts/check_costs.sh
   ```

2. **Check Cost Explorer**
   ```bash
   aws ce get-cost-and-usage \
     --time-period Start=2026-02-01,End=2026-02-28 \
     --granularity DAILY \
     --metrics UnblendedCost \
     --group-by Type=DIMENSION,Key=SERVICE
   ```

3. **Check for orphaned resources**
   ```bash
   ./scripts/verify_cleanup.sh
   ```

4. **Common culprits:**
   - Simulator running 24/7
   - No TTL on DynamoDB tables
   - No S3 lifecycle policies
   - CloudWatch Logs not expiring
   - Multiple deployments in different regions

---

## Cleanup Issues

### Terraform destroy fails

**Symptom:**
```
Error: Error deleting S3 bucket: BucketNotEmpty
```

**Solution:**
```bash
# Empty S3 bucket first
aws s3 rm s3://BUCKET_NAME --recursive

# Then destroy
cd terraform
terraform destroy
```

---

### Resources still exist after teardown

**Symptom:**
verify_cleanup.sh reports remaining resources

**Solution:**
```bash
# Manual cleanup commands

# Delete S3 bucket
aws s3 rb s3://BUCKET_NAME --force

# Delete DynamoDB table
aws dynamodb delete-table --table-name TABLE_NAME

# Delete Lambda function
aws lambda delete-function --function-name FUNCTION_NAME

# Delete IoT Thing
aws iot delete-thing --thing-name THING_NAME

# Delete IoT Certificate
aws iot update-certificate --certificate-id CERT_ID --new-status INACTIVE
aws iot delete-certificate --certificate-id CERT_ID

# Delete CloudWatch Log Group
aws logs delete-log-group --log-group-name LOG_GROUP_NAME
```

---

## Getting Help

### CloudWatch Logs

**View Lambda logs:**
```bash
# Tail logs in real-time
aws logs tail /aws/lambda/kia-paintshop-ingest --follow

# Search logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/kia-paintshop-ingest \
  --filter-pattern "ERROR"
```

### AWS Support

**Create support case:**
1. Go to AWS Support Center
2. Create case
3. Select "Technical Support"
4. Provide details and logs

### Debug Mode

**Enable debug logging:**
```python
# In Lambda functions
import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
```

```bash
# In simulator
python simulator/simulator.py --log-level DEBUG
```

### Useful Commands

```bash
# Check AWS service status
curl https://status.aws.amazon.com/

# Test AWS credentials
aws sts get-caller-identity

# List all resources
aws resourcegroupstaggingapi get-resources \
  --tag-filters Key=Project,Values=kia-paintshop-iot

# Check Lambda function status
aws lambda get-function --function-name FUNCTION_NAME

# Check DynamoDB table status
aws dynamodb describe-table --table-name TABLE_NAME

# Check API Gateway deployment
aws apigateway get-rest-apis
```

---

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `AccessDeniedException` | Insufficient IAM permissions | Add required permissions to IAM user/role |
| `ResourceNotFoundException` | Resource doesn't exist | Verify resource name and region |
| `ValidationException` | Invalid parameter | Check parameter format and values |
| `ThrottlingException` | Too many requests | Implement exponential backoff |
| `ServiceUnavailableException` | AWS service issue | Retry after delay, check AWS status |
| `InvalidParameterValueException` | Invalid parameter value | Verify parameter meets requirements |
| `ResourceInUseException` | Resource already exists | Use different name or delete existing |

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0

For additional help, check:
- `README.md` - Project overview
- `docs/API.md` - API documentation
- `docs/VARIABLES.md` - Variable configuration
- `docs/COSTS.md` - Cost analysis
- AWS Documentation: https://docs.aws.amazon.com/
