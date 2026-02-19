# DynamoDB Tables Configuration

This document describes the DynamoDB tables created for the KIA Paint Shop IoT Prototype.

## Tables Overview

All tables are configured with:
- **Billing Mode**: On-demand (PAY_PER_REQUEST) to minimize costs
- **Encryption**: Server-side encryption enabled
- **Point-in-time Recovery**: Enabled for data protection
- **Tags**: Consistent project tags applied

## 1. sensor-data Table

**Purpose**: Store real-time sensor data with 30-day TTL

**Schema**:
- **PK** (String): `{area}#{variable_id}` - Partition Key
- **SK** (String): `DATA#{timestamp_ms}` - Sort Key
- **TTL**: 30 days (configured via `ttl` attribute)

**Attributes**:
- variable_id (String)
- area (String)
- timestamp (String) - ISO 8601 format
- value (Number)
- unit (String)
- quality (String)
- metadata (Map)

**Global Secondary Indexes**:
1. **GSI1-area-timestamp**
   - PK: area
   - SK: timestamp
   - Projection: ALL
   - Use case: Query all variables in an area by time range

2. **GSI2-variable-timestamp**
   - PK: variable_id
   - SK: timestamp
   - Projection: ALL
   - Use case: Query specific variable data by time range

**Access Patterns**:
- Get data for a variable in time range: Query by PK + SK range
- Get latest N data points for a variable: Query by PK + SK descending limit N
- Get all variables in an area: Query GSI1

## 2. alarms Table

**Purpose**: Store system alarms with status tracking

**Schema**:
- **PK** (String): `ALARM#{alarm_id}` - Partition Key
- **SK** (String): `METADATA` - Sort Key

**Attributes**:
- alarm_id (String) - UUID
- variable_id (String)
- area (String)
- severity (String) - warning, critical
- status (String) - active, acknowledged, resolved
- message (String)
- value (Number)
- threshold (Number)
- created_at (String) - ISO 8601
- acknowledged_at (String, optional)
- resolved_at (String, optional)
- acknowledged_by (String, optional)

**Global Secondary Indexes**:
1. **GSI1-status-created**
   - PK: status
   - SK: created_at
   - Projection: ALL
   - Use case: Query alarms by status (e.g., all active alarms)

2. **GSI2-variable-created**
   - PK: variable_id
   - SK: created_at
   - Projection: ALL
   - Use case: Query all alarms for a specific variable

**Access Patterns**:
- Get active alarms: Query GSI1 where status = 'active'
- Get alarms for a variable: Query GSI2
- Update alarm status: Update item by PK

## 3. statistics Table

**Purpose**: Store aggregated statistics with 7-day TTL

**Schema**:
- **PK** (String): `{variable_id}` - Partition Key
- **SK** (String): `STATS#{window_start}` - Sort Key
- **TTL**: 7 days (configured via `ttl` attribute)

**Attributes**:
- variable_id (String)
- window_start (String) - ISO 8601
- window_end (String) - ISO 8601
- window_minutes (Number)
- count (Number)
- avg (Number)
- min (Number)
- max (Number)
- stddev (Number)

**Access Patterns**:
- Get latest statistics for a variable: Query by PK + SK descending limit 1
- Get statistics history: Query by PK + SK range

## 4. variables-metadata Table

**Purpose**: Store metadata for all 100 system variables

**Schema**:
- **PK** (String): `VAR#{variable_id}` - Partition Key
- **SK** (String): `METADATA` - Sort Key

**Attributes**:
- variable_id (String) - e.g., "PT-TEMP-001"
- name (String) - Descriptive name
- area (String) - pre-treatment, e-coat, production-control
- unit (String) - Unit of measurement
- data_type (String) - float, int, boolean
- min_range (Number)
- max_range (Number)
- alarm_low (Number)
- alarm_high (Number)
- description (String)
- source_file (String) - Source CSV file
- active (Boolean)

**Global Secondary Indexes**:
1. **GSI1-area-variable**
   - PK: area
   - SK: variable_id
   - Projection: ALL
   - Use case: List all variables in an area

**Access Patterns**:
- Get metadata for a variable: Get item by PK
- List all variables: Scan (acceptable, only ~100 items)
- List variables by area: Query GSI1

## Cost Considerations

With on-demand billing mode:
- **Storage**: First 25GB free, then $0.25/GB-month
- **Read requests**: $0.25 per million requests
- **Write requests**: $1.25 per million requests

**Estimated monthly costs** (30 variables, 5-min intervals):
- Storage: ~500 MB (well within free tier)
- Reads: ~1M requests = $0.25
- Writes: ~300K requests = $0.38
- **Total**: ~$0.63/month for DynamoDB

## Terraform Resources

The tables are defined in `terraform/dynamodb.tf` and can be deployed with:

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Table names are exported as Terraform outputs:
- `dynamodb_sensor_data_table`
- `dynamodb_alarms_table`
- `dynamodb_statistics_table`
- `dynamodb_variables_metadata_table`

## Validation Checklist

- [x] All 4 tables defined with correct schemas
- [x] PK and SK configured for each table
- [x] GSI indexes created for required access patterns
- [x] TTL configured for sensor-data (30 days) and statistics (7 days)
- [x] On-demand billing mode configured
- [x] Server-side encryption enabled
- [x] Point-in-time recovery enabled
- [x] Consistent tags applied
- [x] Outputs configured in outputs.tf
