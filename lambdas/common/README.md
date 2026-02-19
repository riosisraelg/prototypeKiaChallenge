# Common Lambda Utilities

This directory contains shared utilities used across all Lambda functions in the KIA Paint Shop IoT Prototype.

## Modules

### metrics.py

Provides centralized CloudWatch custom metrics functionality.

**Features:**
- Send custom metrics to CloudWatch with proper dimensions
- Automatic batching (max 20 metrics per API call)
- Context manager support for automatic flushing
- Convenience methods for success, error, and latency metrics
- Decorator for automatic operation tracking

**Usage:**

```python
from common.metrics import MetricsClient

# Basic usage
metrics = MetricsClient('ingest')
metrics.put_metric('MessagesProcessed', 1, unit='Count')
metrics.put_success_metric('Ingest')
metrics.put_latency_metric('Ingest', 150.5)
metrics.flush()

# Context manager (auto-flush)
with MetricsClient('process') as metrics:
    metrics.put_metric('AlarmsGenerated', 1)
    metrics.put_error_metric('ProcessAlarm', 'ValidationError')

# Decorator
from common.metrics import track_operation

@track_operation('statistics', 'CalculateStats')
def calculate_statistics(data):
    # Your code here
    pass
```

**Metrics Namespace:** `KIA/PaintShop`

**Standard Dimensions:**
- `FunctionName`: Lambda function name
- `Operation`: Operation being performed
- `Status`: Success or Error
- `ErrorType`: Type of error (for error metrics)

### logger.py

Provides structured JSON logging for CloudWatch.

**Features:**
- JSON-formatted log output
- Standardized fields (timestamp, level, message, context, source)
- Automatic error type and stack trace capture
- Lambda request ID tracking
- Convenience methods for logging with context

**Usage:**

```python
from common.logger import get_logger, log_lambda_event, log_lambda_result

# Get logger
logger = get_logger(__name__)

# Basic logging
logger.info("Processing message")
logger.warning("Threshold exceeded", extra={'value': 85, 'threshold': 80})
logger.error("Failed to process", exc_info=True)

# Convenience methods
logger.info_with_context("Processing started", variable_id='PT-001', value=65.5)
logger.error_with_context("Processing failed", exc_info=True, variable_id='PT-001')

# Lambda lifecycle logging
def handler(event, context):
    log_lambda_event(logger, event, context)
    
    start_time = time.time()
    try:
        # Your code here
        duration_ms = (time.time() - start_time) * 1000
        log_lambda_result(logger, context, success=True, duration_ms=duration_ms)
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        log_lambda_result(logger, context, success=False, duration_ms=duration_ms)
        raise
```

**Log Format:**

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "ERROR",
  "message": "Failed to process message",
  "logger": "lambdas.ingest.handler",
  "context": {
    "variable_id": "PT-TEMP-001",
    "value": 65.5,
    "error_type": "ValidationError",
    "error_message": "Invalid value"
  },
  "source": {
    "file": "handler.py",
    "function": "process_message",
    "line": 123
  },
  "stack_trace": "Traceback (most recent call last)...",
  "aws_request_id": "abc-123-def"
}
```

## Installation

These utilities are designed to be deployed as a Lambda Layer or included directly in Lambda function packages.

### Option 1: Lambda Layer (Recommended)

```bash
# Create layer package
mkdir -p layer/python/common
cp lambdas/common/*.py layer/python/common/
cd layer
zip -r common-layer.zip python/

# Deploy layer with Terraform
# (See terraform/lambda_layer.tf)
```

### Option 2: Include in Function Package

```bash
# Copy common utilities to each Lambda function
cp -r lambdas/common lambdas/ingest/
cp -r lambdas/common lambdas/process/
cp -r lambdas/common lambdas/statistics/
```

## Testing

Property-based tests are available:

```bash
# Test metrics
pytest tests/property/test_properties_metrics.py -v --hypothesis-show-statistics

# Test logging
pytest tests/property/test_properties_logging.py -v --hypothesis-show-statistics
```

## Requirements

- boto3 >= 1.34.0 (AWS SDK)
- Python 3.11+

## Cost Considerations

**CloudWatch Metrics:**
- First 10 custom metrics: Free
- Additional metrics: $0.30 per metric per month
- Current usage: ~5-10 custom metrics
- Estimated cost: $0-1/month

**CloudWatch Logs:**
- First 5 GB: Free
- Additional: $0.50 per GB
- Log retention: 7 days (configurable)
- Estimated cost: $0-0.50/month

**Total monitoring cost: ~$0.50-1.50/month**

## Best Practices

1. **Metrics:**
   - Use context managers for automatic flushing
   - Batch metrics when possible (automatic with MetricsClient)
   - Use standard dimension names for consistency
   - Limit custom dimensions to avoid metric explosion

2. **Logging:**
   - Use structured logging for all Lambda functions
   - Include relevant context in extra fields
   - Log errors with exc_info=True for stack traces
   - Set appropriate log levels (DEBUG for development, INFO for production)
   - Use log_lambda_event and log_lambda_result for lifecycle tracking

3. **Performance:**
   - Metrics are sent asynchronously (non-blocking)
   - Logging is synchronous but fast
   - Batch operations when possible
   - Flush metrics at end of Lambda execution

## Troubleshooting

**Metrics not appearing in CloudWatch:**
- Check IAM permissions (cloudwatch:PutMetricData)
- Verify namespace is correct (KIA/PaintShop)
- Check for errors in CloudWatch Logs
- Ensure flush() is called

**Logs not structured:**
- Verify StructuredFormatter is configured
- Check LOG_LEVEL environment variable
- Ensure logger is obtained via get_logger()

**High costs:**
- Review number of custom metrics
- Reduce log retention period
- Filter unnecessary log entries
- Use sampling for high-volume metrics
