# REST API Documentation

Complete API reference for the KIA Paint Shop IoT Prototype REST API.

## Base URL

```
https://{api-id}.execute-api.{region}.amazonaws.com/demo
```

Get your API URL from Terraform outputs:
```bash
cd terraform
terraform output api_url
```

## Authentication

All endpoints require API key authentication via the `x-api-key` header.

```bash
# Get API key from Terraform
terraform output api_key
```

**Example Request:**
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://your-api-url.amazonaws.com/demo/variables
```

## Response Format

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "uuid-here"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message"
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "uuid-here"
}
```

## HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid API key)
- `404` - Not Found (resource doesn't exist)
- `500` - Internal Server Error

---

## Endpoints

### 1. List Variables

Get metadata for all 100 monitored variables.

**Endpoint:** `GET /variables`

**Authentication:** Required

**Parameters:** None

**Response:**
```json
{
  "success": true,
  "data": {
    "variables": [
      {
        "variable_id": "PT_TEMP_TANK_1",
        "variable_name": "Temperature Tank 1",
        "area": "pre-treatment",
        "unit": "°C",
        "min_range": 20.0,
        "max_range": 80.0,
        "alarm_low": 25.0,
        "alarm_high": 75.0
      },
      {
        "variable_id": "ED_VOLTAGE_MAIN",
        "variable_name": "Main Voltage",
        "area": "e-coat",
        "unit": "V",
        "min_range": 200.0,
        "max_range": 400.0,
        "alarm_low": 220.0,
        "alarm_high": 380.0
      }
      // ... 98 more variables
    ],
    "total_count": 100,
    "by_area": {
      "pre-treatment": 48,
      "e-coat": 18,
      "production-control": 34
    }
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "abc-123"
}
```

**Example:**
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  https://your-api-url.amazonaws.com/demo/variables
```

**Use Cases:**
- Populate dashboard variable selector
- Get variable metadata for charts
- Discover available variables

---

### 2. Get Variable Data

Get historical time-series data for a specific variable.

**Endpoint:** `GET /variables/{variable_id}/data`

**Authentication:** Required

**Path Parameters:**
- `variable_id` (required) - Variable identifier (e.g., "PT_TEMP_TANK_1")

**Query Parameters:**
- `start` (optional) - Start timestamp (ISO 8601 format)
- `end` (optional) - End timestamp (ISO 8601 format)
- `limit` (optional) - Maximum number of data points (default: 1000)

**Defaults:**
- If `start` not provided: 1 hour ago
- If `end` not provided: now
- Maximum time range: 7 days

**Response:**
```json
{
  "success": true,
  "data": {
    "variable_id": "PT_TEMP_TANK_1",
    "variable_name": "Temperature Tank 1",
    "area": "pre-treatment",
    "unit": "°C",
    "data_points": [
      {
        "timestamp": "2026-02-19T12:00:00Z",
        "value": 52.3
      },
      {
        "timestamp": "2026-02-19T12:00:30Z",
        "value": 52.5
      },
      {
        "timestamp": "2026-02-19T12:01:00Z",
        "value": 52.1
      }
      // ... more data points
    ],
    "count": 120,
    "time_range": {
      "start": "2026-02-19T11:00:00Z",
      "end": "2026-02-19T12:00:00Z"
    }
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "def-456"
}
```

**Examples:**

Get last hour of data:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/variables/PT_TEMP_TANK_1/data"
```

Get specific time range:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/variables/PT_TEMP_TANK_1/data?start=2026-02-19T10:00:00Z&end=2026-02-19T12:00:00Z"
```

Get last 100 data points:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/variables/PT_TEMP_TANK_1/data?limit=100"
```

**Error Responses:**

Variable not found (404):
```json
{
  "success": false,
  "error": {
    "code": "VARIABLE_NOT_FOUND",
    "message": "Variable 'INVALID_ID' not found"
  }
}
```

Invalid timestamp format (400):
```json
{
  "success": false,
  "error": {
    "code": "INVALID_TIMESTAMP",
    "message": "Timestamp must be in ISO 8601 format"
  }
}
```

**Use Cases:**
- Display time-series charts
- Export historical data
- Analyze trends

---

### 3. List Alarms

Get list of alarms with optional filtering by status.

**Endpoint:** `GET /alarms`

**Authentication:** Required

**Query Parameters:**
- `status` (optional) - Filter by alarm status
  - `active` - Currently active alarms
  - `acknowledged` - Acknowledged but not resolved
  - `resolved` - Resolved alarms
  - If not provided: returns all alarms

**Response:**
```json
{
  "success": true,
  "data": {
    "alarms": [
      {
        "alarm_id": "alarm-uuid-1",
        "variable_id": "PT_TEMP_TANK_1",
        "variable_name": "Temperature Tank 1",
        "area": "pre-treatment",
        "severity": "critical",
        "status": "active",
        "value": 82.5,
        "threshold": 75.0,
        "threshold_type": "high",
        "message": "Temperature exceeds high threshold by 10.0%",
        "created_at": "2026-02-19T12:15:00Z",
        "acknowledged_at": null,
        "acknowledged_by": null
      },
      {
        "alarm_id": "alarm-uuid-2",
        "variable_id": "ED_VOLTAGE_MAIN",
        "variable_name": "Main Voltage",
        "area": "e-coat",
        "severity": "warning",
        "status": "acknowledged",
        "value": 215.0,
        "threshold": 220.0,
        "threshold_type": "low",
        "message": "Voltage below low threshold by 2.3%",
        "created_at": "2026-02-19T12:10:00Z",
        "acknowledged_at": "2026-02-19T12:20:00Z",
        "acknowledged_by": "operator-1"
      }
    ],
    "total_count": 2,
    "by_status": {
      "active": 1,
      "acknowledged": 1,
      "resolved": 0
    },
    "by_severity": {
      "warning": 1,
      "critical": 1
    }
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "ghi-789"
}
```

**Examples:**

Get all alarms:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/alarms"
```

Get only active alarms:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/alarms?status=active"
```

Get acknowledged alarms:
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/alarms?status=acknowledged"
```

**Alarm Severity:**
- `warning` - Exceeds threshold by <10%
- `critical` - Exceeds threshold by ≥10%

**Alarm Status:**
- `active` - Newly detected, not yet acknowledged
- `acknowledged` - Operator has acknowledged the alarm
- `resolved` - Alarm condition no longer exists

**Use Cases:**
- Display active alarms in dashboard
- Alarm history review
- Operator acknowledgment workflow

---

### 4. Acknowledge Alarm

Mark an alarm as acknowledged by an operator.

**Endpoint:** `POST /alarms/{alarm_id}/acknowledge`

**Authentication:** Required

**Path Parameters:**
- `alarm_id` (required) - Alarm identifier (UUID)

**Request Body:**
```json
{
  "acknowledged_by": "operator-1"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "alarm_id": "alarm-uuid-1",
    "variable_id": "PT_TEMP_TANK_1",
    "status": "acknowledged",
    "acknowledged_at": "2026-02-19T12:30:00Z",
    "acknowledged_by": "operator-1"
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "jkl-012"
}
```

**Example:**
```bash
curl -X POST \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by":"operator-1"}' \
  "https://your-api-url.amazonaws.com/demo/alarms/alarm-uuid-1/acknowledge"
```

**Error Responses:**

Alarm not found (404):
```json
{
  "success": false,
  "error": {
    "code": "ALARM_NOT_FOUND",
    "message": "Alarm 'invalid-id' not found"
  }
}
```

Alarm already acknowledged (400):
```json
{
  "success": false,
  "error": {
    "code": "ALARM_ALREADY_ACKNOWLEDGED",
    "message": "Alarm already acknowledged at 2026-02-19T12:20:00Z"
  }
}
```

**Use Cases:**
- Operator acknowledges alarm in dashboard
- Track alarm response times
- Audit trail for alarm handling

---

### 5. Get Statistics

Get aggregated statistics for a variable over the last 24 hours.

**Endpoint:** `GET /statistics/{variable_id}`

**Authentication:** Required

**Path Parameters:**
- `variable_id` (required) - Variable identifier

**Response:**
```json
{
  "success": true,
  "data": {
    "variable_id": "PT_TEMP_TANK_1",
    "variable_name": "Temperature Tank 1",
    "unit": "°C",
    "time_range": {
      "start": "2026-02-18T12:30:00Z",
      "end": "2026-02-19T12:30:00Z"
    },
    "statistics": {
      "mean": 52.3,
      "min": 48.1,
      "max": 56.7,
      "stddev": 2.1,
      "count": 2880,
      "last_value": 52.5,
      "last_updated": "2026-02-19T12:30:00Z"
    },
    "hourly_aggregates": [
      {
        "hour": "2026-02-19T11:00:00Z",
        "mean": 52.1,
        "min": 50.2,
        "max": 54.3,
        "count": 120
      },
      {
        "hour": "2026-02-19T12:00:00Z",
        "mean": 52.5,
        "min": 51.1,
        "max": 53.8,
        "count": 60
      }
      // ... 22 more hours
    ]
  },
  "timestamp": "2026-02-19T12:30:00Z",
  "request_id": "mno-345"
}
```

**Example:**
```bash
curl -H "x-api-key: YOUR_API_KEY" \
  "https://your-api-url.amazonaws.com/demo/statistics/PT_TEMP_TANK_1"
```

**Statistics Calculated:**
- `mean` - Average value
- `min` - Minimum value
- `max` - Maximum value
- `stddev` - Standard deviation
- `count` - Number of data points
- `last_value` - Most recent value
- `last_updated` - Timestamp of last value

**Update Frequency:**
- Statistics are calculated every 5 minutes
- Covers last 10 minutes of data
- Stored with 7-day TTL in DynamoDB

**Use Cases:**
- Display summary statistics cards
- Trend analysis
- Quality control monitoring

---

## Rate Limits

**API Gateway Limits:**
- 1000 requests per day per API key
- 100 requests per second (burst: 200)
- Throttling returns HTTP 429

**Recommendations:**
- Use dashboard auto-refresh: 30 seconds
- Batch requests when possible
- Cache responses client-side

---

## CORS Configuration

CORS is enabled for all origins to support dashboard access.

**Allowed Methods:**
- GET
- POST
- OPTIONS (preflight)

**Allowed Headers:**
- Content-Type
- x-api-key

**Exposed Headers:**
- Content-Type

---

## Error Codes

| Code | Description |
|------|-------------|
| `UNAUTHORIZED` | Missing or invalid API key |
| `INVALID_PARAMETER` | Invalid query parameter |
| `INVALID_TIMESTAMP` | Timestamp not in ISO 8601 format |
| `VARIABLE_NOT_FOUND` | Variable ID doesn't exist |
| `ALARM_NOT_FOUND` | Alarm ID doesn't exist |
| `ALARM_ALREADY_ACKNOWLEDGED` | Alarm was already acknowledged |
| `INTERNAL_ERROR` | Server-side error |

---

## Best Practices

### 1. API Key Security
```bash
# Store API key in environment variable
export API_KEY="your-api-key-here"

# Use in requests
curl -H "x-api-key: $API_KEY" ...
```

### 2. Timestamp Format
Always use ISO 8601 format with timezone:
```
2026-02-19T12:30:00Z  ✓ Correct
2026-02-19 12:30:00   ✗ Wrong
```

### 3. Error Handling
```javascript
try {
  const response = await fetch(url, {
    headers: { 'x-api-key': apiKey }
  });
  
  const data = await response.json();
  
  if (!data.success) {
    console.error('API Error:', data.error.message);
    // Handle error
  }
} catch (error) {
  console.error('Network Error:', error);
  // Handle network error
}
```

### 4. Pagination
For large datasets, use `limit` parameter:
```bash
# Get first 100 points
curl "...?limit=100"

# Get next 100 points (use last timestamp)
curl "...?start=2026-02-19T12:00:00Z&limit=100"
```

---

## Testing with curl

### Get API credentials
```bash
cd terraform
API_URL=$(terraform output -raw api_url)
API_KEY=$(terraform output -raw api_key)
```

### Test all endpoints
```bash
# 1. List variables
curl -H "x-api-key: $API_KEY" "$API_URL/variables"

# 2. Get variable data
curl -H "x-api-key: $API_KEY" "$API_URL/variables/PT_TEMP_TANK_1/data"

# 3. List alarms
curl -H "x-api-key: $API_KEY" "$API_URL/alarms"

# 4. Acknowledge alarm (replace alarm-id)
curl -X POST \
  -H "x-api-key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"acknowledged_by":"test-user"}' \
  "$API_URL/alarms/ALARM_ID/acknowledge"

# 5. Get statistics
curl -H "x-api-key: $API_KEY" "$API_URL/statistics/PT_TEMP_TANK_1"
```

---

## Integration Examples

### JavaScript/TypeScript
```typescript
const API_URL = process.env.REACT_APP_API_URL;
const API_KEY = process.env.REACT_APP_API_KEY;

async function getVariables() {
  const response = await fetch(`${API_URL}/variables`, {
    headers: {
      'x-api-key': API_KEY
    }
  });
  
  const data = await response.json();
  return data.data.variables;
}
```

### Python
```python
import requests

API_URL = os.environ['API_URL']
API_KEY = os.environ['API_KEY']

def get_variables():
    response = requests.get(
        f'{API_URL}/variables',
        headers={'x-api-key': API_KEY}
    )
    return response.json()['data']['variables']
```

---

## Troubleshooting

### 401 Unauthorized
- Verify API key is correct
- Check `x-api-key` header is set
- Ensure API key is associated with usage plan

### 404 Not Found
- Verify endpoint URL is correct
- Check variable_id or alarm_id exists
- Ensure stage name is "demo"

### 429 Too Many Requests
- Reduce request frequency
- Implement exponential backoff
- Check usage plan limits

### 500 Internal Server Error
- Check CloudWatch Logs for Lambda errors
- Verify DynamoDB tables exist
- Check IAM permissions

---

**Last Updated:** February 19, 2026  
**Version:** 1.0.0  
**API Version:** v1
