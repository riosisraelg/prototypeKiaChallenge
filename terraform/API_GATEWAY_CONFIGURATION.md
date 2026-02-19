# API Gateway Configuration Guide

## Overview

This document describes the API Gateway configuration for the KIA Paint Shop IoT Prototype. The API Gateway provides a REST API interface for the dashboard to query sensor data, alarms, and statistics.

## Architecture

```
Dashboard (React) 
    ↓ HTTPS + API Key
API Gateway (REST API)
    ↓ Lambda Proxy Integration
Lambda Functions (API Handlers)
    ↓ SDK Calls
DynamoDB Tables + S3 Bucket
```

## API Endpoints

### Base URL
After deployment, the API will be available at:
```
https://{api-id}.execute-api.us-east-1.amazonaws.com/demo
```

The exact URL is exported in Terraform outputs as `api_url`.

### Endpoints

| Method | Path | Handler | Description |
|--------|------|---------|-------------|
| GET | `/variables` | `list_variables.py` | List all 100 variables with metadata |
| GET | `/variables/{id}/data` | `get_variable_data.py` | Get historical data for a variable |
| GET | `/alarms` | `list_alarms.py` | List alarms (filterable by status) |
| POST | `/alarms/{id}/acknowledge` | `acknowledge_alarm.py` | Acknowledge an alarm |
| GET | `/statistics/{variable_id}` | `get_statistics.py` | Get statistics for a variable |

## Authentication

All endpoints require API Key authentication using the `x-api-key` header.

### Getting the API Key

After running `terraform apply`, retrieve the API key:

```bash
# Get API key (sensitive output)
terraform output -raw api_key

# Or export it to environment variable
export API_KEY=$(terraform output -raw api_key)
```

### Using the API Key

Include the API key in all requests:

```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://your-api-url.execute-api.us-east-1.amazonaws.com/demo/variables
```

## Usage Limits

The API has the following limits configured:

- **Daily Quota**: 1,000 requests per day
- **Rate Limit**: 100 requests per second
- **Burst Limit**: 200 requests

These limits are enforced by the Usage Plan associated with the API Key.

## CORS Configuration

CORS is enabled for all endpoints to allow dashboard access from any origin:

- **Allowed Origins**: `*` (all origins)
- **Allowed Methods**: `GET, POST, OPTIONS`
- **Allowed Headers**: `Content-Type, X-Amz-Date, Authorization, X-Api-Key, X-Amz-Security-Token, x-api-key`

## Lambda Functions

### Shared Configuration

All API Lambda functions share:
- **Runtime**: Python 3.11
- **Memory**: 256 MB
- **Timeout**: 30 seconds
- **IAM Role**: `kia-paintshop-prototype-lambda-api-role`

### Environment Variables

Each Lambda function has access to:
- `DYNAMODB_*_TABLE`: Relevant DynamoDB table names
- `S3_ARCHIVE_BUCKET`: S3 bucket for archived data (get_variable_data only)
- `LOG_LEVEL`: Logging level (INFO)
- `CLOUDWATCH_NAMESPACE`: CloudWatch metrics namespace (KIA/PaintShop)

### IAM Permissions

The Lambda API role has permissions for:
- **CloudWatch Logs**: Create log groups/streams, put log events
- **DynamoDB**: GetItem, Query, Scan, UpdateItem on all tables
- **S3**: GetObject, ListBucket on archive bucket
- **CloudWatch Metrics**: PutMetricData to KIA/PaintShop namespace

## Deployment

### Initial Deployment

```bash
cd terraform
terraform init
terraform apply
```

The deployment will:
1. Create the API Gateway REST API
2. Configure all resources and methods
3. Set up CORS for all endpoints
4. Create and configure Lambda functions
5. Generate and configure API Key
6. Create Usage Plan with limits
7. Deploy to "demo" stage
8. Enable CloudWatch logging

### Redeployment

The API Gateway deployment is configured to automatically redeploy when:
- Any resource or method changes
- Any integration changes
- Lambda function code changes

Simply run `terraform apply` again to update.

## Testing the API

### 1. Get API URL and Key

```bash
export API_URL=$(terraform output -raw api_url)
export API_KEY=$(terraform output -raw api_key)
```

### 2. Test Each Endpoint

#### List Variables
```bash
curl -H "x-api-key: $API_KEY" \
  "$API_URL/variables"
```

Expected response:
```json
{
  "success": true,
  "data": [
    {
      "variable_id": "PT-TEMP-001",
      "name": "Temperature Tank 1",
      "area": "pre-treatment",
      "unit": "°C",
      ...
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z",
  "request_id": "abc-123"
}
```

#### Get Variable Data
```bash
curl -H "x-api-key: $API_KEY" \
  "$API_URL/variables/PT-TEMP-001/data?start=2024-01-15T10:00:00Z&end=2024-01-15T11:00:00Z"
```

#### List Alarms
```bash
# All alarms
curl -H "x-api-key: $API_KEY" \
  "$API_URL/alarms"

# Active alarms only
curl -H "x-api-key: $API_KEY" \
  "$API_URL/alarms?status=active"
```

#### Acknowledge Alarm
```bash
curl -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  "$API_URL/alarms/ALARM_ID/acknowledge"
```

#### Get Statistics
```bash
curl -H "x-api-key: $API_KEY" \
  "$API_URL/statistics/PT-TEMP-001"
```

## Monitoring

### CloudWatch Logs

API Gateway logs are available at:
```
/aws/apigateway/kia-paintshop-prototype
```

Lambda function logs are available at:
```
/aws/lambda/kia-paintshop-prototype-api-list-variables
/aws/lambda/kia-paintshop-prototype-api-get-variable-data
/aws/lambda/kia-paintshop-prototype-api-list-alarms
/aws/lambda/kia-paintshop-prototype-api-acknowledge-alarm
/aws/lambda/kia-paintshop-prototype-api-get-statistics
```

### CloudWatch Metrics

API Gateway automatically publishes metrics:
- `Count`: Number of API calls
- `4XXError`: Client errors
- `5XXError`: Server errors
- `Latency`: Request latency
- `IntegrationLatency`: Lambda execution time

View metrics in CloudWatch console under:
- Namespace: `AWS/ApiGateway`
- Dimensions: `ApiName=kia-paintshop-prototype-api`

### X-Ray Tracing

X-Ray tracing is enabled for the API Gateway stage. View traces in the AWS X-Ray console to debug performance issues.

## Troubleshooting

### 403 Forbidden - Missing API Key

**Problem**: Request returns 403 Forbidden

**Solution**: Ensure you're including the API key in the `x-api-key` header:
```bash
curl -H "x-api-key: YOUR_API_KEY" ...
```

### 403 Forbidden - Invalid API Key

**Problem**: API key is included but still getting 403

**Solution**: 
1. Verify the API key is correct: `terraform output -raw api_key`
2. Check that the Usage Plan is associated with the API Key
3. Verify the API Key is enabled in AWS Console

### 429 Too Many Requests

**Problem**: Request returns 429 Too Many Requests

**Solution**: You've exceeded the rate limit (100 req/s) or daily quota (1000 req/day). Wait and retry, or increase limits in `variables.tf`:
```hcl
variable "api_throttle_rate_limit" {
  default = 100  # Increase this
}
```

### 500 Internal Server Error

**Problem**: API returns 500 error

**Solution**:
1. Check Lambda function logs in CloudWatch
2. Verify DynamoDB tables exist and have data
3. Check Lambda IAM permissions
4. Review API Gateway execution logs

### CORS Errors in Browser

**Problem**: Browser shows CORS error when calling API

**Solution**:
1. Verify OPTIONS method is configured for the endpoint
2. Check CORS headers in API Gateway method response
3. Ensure `Access-Control-Allow-Origin: *` is set
4. Clear browser cache and retry

### Lambda Function Not Found

**Problem**: API Gateway returns error about Lambda function not existing

**Solution**:
1. Verify Lambda functions were created: `terraform state list | grep lambda_function.api`
2. Check Lambda permissions for API Gateway to invoke
3. Redeploy: `terraform apply`

## Cost Considerations

### API Gateway Costs

- **Free Tier**: 1 million API calls per month for 12 months
- **After Free Tier**: $3.50 per million API calls
- **Data Transfer**: $0.09 per GB out

### Expected Costs for Prototype

With estimated usage:
- 100,000 API calls/month (dashboard + testing)
- Within free tier: **$0/month**
- After free tier: **$0.35/month**

### Cost Optimization Tips

1. **Cache responses**: Enable API Gateway caching for frequently accessed data
2. **Reduce polling**: Increase dashboard refresh interval from 30s to 60s
3. **Batch requests**: Combine multiple variable queries into single requests
4. **Use WebSockets**: For real-time updates, consider API Gateway WebSocket API

## Security Best Practices

### API Key Management

1. **Never commit API keys to git**: Use environment variables or secrets manager
2. **Rotate keys regularly**: Generate new API keys periodically
3. **Use separate keys per environment**: Different keys for dev/staging/prod
4. **Monitor usage**: Set up CloudWatch alarms for unusual API usage patterns

### Additional Security Measures

1. **Enable AWS WAF**: Add Web Application Firewall for DDoS protection (costs extra)
2. **Restrict CORS origins**: Change `Access-Control-Allow-Origin` from `*` to specific domain
3. **Add request validation**: Enable API Gateway request validation for input sanitization
4. **Use resource policies**: Restrict API access to specific IP ranges or VPCs

## Next Steps

After configuring API Gateway:

1. **Test all endpoints**: Use the curl commands above to verify each endpoint works
2. **Configure dashboard**: Update dashboard environment variables with API URL and key
3. **Monitor usage**: Check CloudWatch metrics to ensure API is working correctly
4. **Set up alarms**: Create CloudWatch alarms for high error rates or latency

## References

- [AWS API Gateway Documentation](https://docs.aws.amazon.com/apigateway/)
- [API Gateway REST API Reference](https://docs.aws.amazon.com/apigateway/latest/api/API_Operations.html)
- [API Gateway Pricing](https://aws.amazon.com/api-gateway/pricing/)
- [Lambda Proxy Integration](https://docs.aws.amazon.com/apigateway/latest/developerguide/set-up-lambda-proxy-integrations.html)
