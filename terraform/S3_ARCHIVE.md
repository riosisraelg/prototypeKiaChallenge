# S3 Archive Bucket Configuration

## Overview

This document describes the S3 bucket configuration for archiving historical IoT sensor data from the KIA Paint Shop prototype.

## Bucket Details

- **Bucket Name**: `kia-paintshop-prototype-archive-{account-id}`
- **Purpose**: Long-term storage of historical sensor data, alarms, and statistics
- **Region**: Same as other AWS resources (default: us-east-1)

## Security Configuration

### Encryption at Rest
- **Algorithm**: AES256 (AWS managed keys)
- **Bucket Key**: Enabled for cost optimization
- **Rationale**: Using AWS managed keys instead of KMS to avoid additional costs while maintaining data security

### Public Access
All public access is blocked:
- `block_public_acls`: true
- `block_public_policy`: true
- `ignore_public_acls`: true
- `restrict_public_buckets`: true

## Lifecycle Policies

The bucket implements three lifecycle rules to manage costs:

### 1. Raw Sensor Data (`raw-data/` prefix)
- **Transition to Glacier**: After 60 days
- **Deletion**: After 90 days
- **Incomplete Multipart Upload Cleanup**: After 7 days

### 2. Alarms Data (`alarms/` prefix)
- **Transition to Glacier**: After 60 days
- **Deletion**: After 90 days
- **Incomplete Multipart Upload Cleanup**: After 7 days

### 3. Statistics Data (`statistics/` prefix)
- **Transition to Glacier**: After 60 days
- **Deletion**: After 90 days
- **Incomplete Multipart Upload Cleanup**: After 7 days

## Data Structure

The bucket uses a partitioned structure optimized for Athena queries:

```
s3://kia-paintshop-prototype-archive-{account-id}/
├── raw-data/
│   └── year=YYYY/
│       └── month=MM/
│           └── day=DD/
│               └── area={area-name}/
│                   └── data.parquet.gz
├── alarms/
│   └── year=YYYY/
│       └── month=MM/
│           └── alarms.json.gz
└── statistics/
    └── year=YYYY/
        └── month=MM/
            └── stats.parquet.gz
```

### Partition Keys

**Raw Data Partitions**:
- `year`: 4-digit year (e.g., 2024)
- `month`: 2-digit month (e.g., 01, 12)
- `day`: 2-digit day (e.g., 01, 31)
- `area`: Process area name
  - `pre-treatment`
  - `e-coat`
  - `production-control`

**Benefits**:
- Efficient querying by time range
- Reduced scan costs in Athena
- Logical organization for data management
- Easy to implement retention policies

## File Formats

### Raw Sensor Data
- **Format**: Apache Parquet
- **Compression**: gzip
- **Schema**: Same as DynamoDB sensor-data table
  ```
  - variable_id: string
  - area: string
  - timestamp: string (ISO 8601)
  - value: double
  - unit: string
  - quality: string
  - metadata: struct
  ```

### Alarms
- **Format**: JSON (newline-delimited)
- **Compression**: gzip
- **Schema**: Same as DynamoDB alarms table

### Statistics
- **Format**: Apache Parquet
- **Compression**: gzip
- **Schema**: Same as DynamoDB statistics table

## Cost Optimization

### Storage Costs (Estimated)
- **Standard Storage**: ~$0.023/GB/month
- **Glacier Storage**: ~$0.004/GB/month (after 60 days)
- **Expected Monthly Data**: ~500 MB
- **Monthly Cost**: ~$0.01 (Standard) + negligible (Glacier)

### Data Transfer
- **Ingress**: Free
- **Egress**: First 1 GB free, then $0.09/GB
- **Expected Usage**: Minimal (data queried infrequently)

### Request Costs
- **PUT Requests**: $0.005 per 1,000 requests
- **GET Requests**: $0.0004 per 1,000 requests
- **Expected Monthly**: ~10K PUT, ~50K GET = ~$0.07

**Total Estimated S3 Cost**: ~$0.10/month

## Archiving Process

### From DynamoDB to S3

Data archiving will be implemented in a future task using Lambda:

1. **Trigger**: EventBridge scheduled rule (daily)
2. **Lambda Function**: Query DynamoDB for data older than 30 days
3. **Processing**:
   - Convert to Parquet format
   - Compress with gzip
   - Partition by year/month/day/area
4. **Upload**: Write to S3 with appropriate prefix
5. **Cleanup**: Delete archived data from DynamoDB

### Manual Archiving (for testing)

```bash
# Example: Archive sensor data for a specific date
aws dynamodb query \
  --table-name kia-paintshop-prototype-sensor-data \
  --key-condition-expression "PK = :pk AND SK BETWEEN :start AND :end" \
  --expression-attribute-values '{
    ":pk": {"S": "pre-treatment#PT-TEMP-001"},
    ":start": {"S": "DATA#1705305600000"},
    ":end": {"S": "DATA#1705391999999"}
  }' \
  --output json > data.json

# Convert to Parquet and upload (requires Python script)
python scripts/archive_to_s3.py \
  --input data.json \
  --bucket kia-paintshop-prototype-archive-{account-id} \
  --prefix raw-data/year=2024/month=01/day=15/area=pre-treatment/
```

## Querying with Athena (Future Enhancement)

Once data is in S3, it can be queried using Amazon Athena:

```sql
-- Create external table
CREATE EXTERNAL TABLE sensor_data_archive (
  variable_id STRING,
  area STRING,
  timestamp STRING,
  value DOUBLE,
  unit STRING,
  quality STRING
)
PARTITIONED BY (
  year INT,
  month INT,
  day INT,
  area_partition STRING
)
STORED AS PARQUET
LOCATION 's3://kia-paintshop-prototype-archive-{account-id}/raw-data/';

-- Add partitions
MSCK REPAIR TABLE sensor_data_archive;

-- Query example
SELECT 
  variable_id,
  AVG(value) as avg_value,
  MIN(value) as min_value,
  MAX(value) as max_value
FROM sensor_data_archive
WHERE year = 2024 
  AND month = 1 
  AND day = 15
  AND area_partition = 'pre-treatment'
GROUP BY variable_id;
```

**Note**: Athena is not included in the initial prototype to minimize costs, but the data structure supports it for future use.

## Cleanup on Teardown

When running `terraform destroy`, the S3 bucket will be deleted. However, if the bucket contains objects, Terraform will fail. Use the cleanup script:

```bash
# Empty bucket before destroy
aws s3 rm s3://kia-paintshop-prototype-archive-{account-id} --recursive

# Then run terraform destroy
terraform destroy
```

The `scripts/teardown.sh` script handles this automatically.

## Monitoring

### CloudWatch Metrics (Standard S3 Metrics)
- `BucketSizeBytes`: Total bucket size
- `NumberOfObjects`: Total object count
- `AllRequests`: Total request count

### Cost Alerts
CloudWatch Alarms will be configured to alert if:
- Bucket size exceeds 20 GB
- Monthly costs exceed $5

## Security Best Practices

1. **Encryption**: All data encrypted at rest with AES256
2. **Access Control**: IAM roles with least privilege
3. **Public Access**: Completely blocked
4. **Audit**: CloudTrail logs all S3 API calls
5. **Versioning**: Disabled to minimize costs (can be enabled if needed)

## References

- [AWS S3 Lifecycle Configuration](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
- [AWS S3 Encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/serv-side-encryption.html)
- [Apache Parquet Format](https://parquet.apache.org/docs/)
- [Amazon Athena Partitioning](https://docs.aws.amazon.com/athena/latest/ug/partitions.html)
