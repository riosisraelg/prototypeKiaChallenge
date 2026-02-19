# API Lambda Handlers

This directory contains Lambda handlers for the REST API endpoints of the KIA Paint Shop IoT Prototype.

## Overview

The API provides endpoints for querying variables, historical data, alarms, and statistics. All handlers follow a consistent response format and error handling pattern.

## Handlers

### GET /variables - `list_variables.py`

Retrieves all 100 variables with their metadata, organized by area.

**Response Format:**
```json
{
  "success": true,
  "data": {
    "variables": {
      "pre-treatment": [
        {
          "variable_id": "PT-001",
          "name": "Temperature Tank 1",
          "area": "pre-treatment",
          "unit": "°C",
          "data_type": "float",
          "min_range": 60.0,
          "max_range": 70.0,
          "alarm_low": 61.0,
          "alarm_high": 69.0,
          "description": "Pre-Treatment - Temperature Tank 1",
          "source_file": "KMX-PA-PT-F-001.csv",
          "active": true
        }
      ],
      "e-coat": [...],
      "production-control": [...]
    },
    "summary": {
      "total": 100,
      "by_area": {
        "pre-treatment": 48,
        "e-coat": 18,
        "production-control": 34
      },
      "active": 100
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "abc-123-def"
}
```

**DynamoDB Table:** `variables-metadata`

**Requirements:** 5.1

### GET /variables/{id}/data - `get_variable_data.py`

Retrieves historical sensor data for a specific variable within a time range.

**Path Parameters:**
- `id`: Variable ID (e.g., "PT-TEMP-001")

**Query Parameters:**
- `start`: Start timestamp in ISO 8601 format (required, e.g., "2024-01-15T10:00:00Z")
- `end`: End timestamp in ISO 8601 format (required, e.g., "2024-01-15T11:00:00Z")
- Maximum range: 7 days

**Response Format:**
```json
{
  "success": true,
  "data": {
    "variable_id": "PT-TEMP-001",
    "area": "pre-treatment",
    "start": "2024-01-15T10:00:00Z",
    "end": "2024-01-15T11:00:00Z",
    "count": 12,
    "data_points": [
      {
        "timestamp": "2024-01-15T10:00:00Z",
        "value": 65.5,
        "unit": "°C",
        "quality": "good",
        "metadata": {
          "min_range": 60.0,
          "max_range": 70.0,
          "alarm_low": 61.0,
          "alarm_high": 69.0
        }
      }
    ],
    "sources": {
      "dynamodb": 12,
      "s3": 0
    }
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "abc-123-def"
}
```

**Data Sources:**
1. **DynamoDB** (primary): Recent data with 30-day TTL
2. **S3** (fallback): Archived data older than 30 days (not yet implemented in MVP)

**DynamoDB Tables:** 
- `sensor-data` (PK: "{area}#{variable_id}", SK: "DATA#{timestamp_ms}")
- `variables-metadata` (for area lookup)

**Requirements:** 5.2, 3.3

## Standard Response Format

All API handlers follow this response structure:

### Success Response (2xx)
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "abc-123-def"
}
```

### Error Response (4xx, 5xx)
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Descripción del error en español"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "abc-123-def"
}
```

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request parameters |
| `UNAUTHORIZED` | 401 | Missing or invalid API key |
| `NOT_FOUND` | 404 | Resource not found |
| `SERVICE_UNAVAILABLE` | 503 | DynamoDB or other AWS service temporarily unavailable |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

## CORS Configuration

All handlers include CORS headers:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Headers: Content-Type,X-Api-Key`
- `Access-Control-Allow-Methods: GET,POST,OPTIONS`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VARIABLES_METADATA_TABLE` | DynamoDB table for variables metadata | `kia-paintshop-variables-metadata` |
| `SENSOR_DATA_TABLE` | DynamoDB table for sensor data | `kia-paintshop-sensor-data` |
| `ALARMS_TABLE` | DynamoDB table for alarms | `kia-paintshop-alarms` |
| `STATISTICS_TABLE` | DynamoDB table for statistics | `kia-paintshop-statistics` |
| `ARCHIVE_BUCKET` | S3 bucket for archived data | (empty - optional) |
| `LOG_LEVEL` | Logging level | `INFO` |

## Testing

Unit tests are located in `tests/unit/test_*.py`.

Run tests:
```bash
python -m pytest tests/unit/test_list_variables.py -v
```

## Deployment

These handlers are deployed as Lambda functions via Terraform. See `terraform/lambda_api.tf` for configuration.

## Authentication

API authentication is handled by API Gateway using API keys. The `x-api-key` header must be included in all requests.

## Logging

All handlers use structured logging with the following fields:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level (INFO, WARNING, ERROR)
- `message`: Log message
- `request_id`: Lambda request ID for tracing
- `context`: Additional context (variable_id, error details, etc.)

Logs are sent to CloudWatch Logs with 7-day retention.

## Performance

- **Cold start**: ~500ms (Python 3.11 runtime)
- **Warm execution**: ~50-100ms
- **Memory**: 256 MB (configurable)
- **Timeout**: 30 seconds

## Cost Optimization

- Uses DynamoDB on-demand pricing (pay per request)
- Scan operations are acceptable for small tables (~100 variables)
- Lambda invocations stay within free tier (1M/month)
- CloudWatch Logs retention limited to 7 days

## Future Enhancements

- [ ] Add caching layer (ElastiCache or API Gateway caching)
- [ ] Implement pagination for large result sets
- [ ] Add query parameter filtering
- [ ] Implement rate limiting per API key
- [ ] Add request/response compression
