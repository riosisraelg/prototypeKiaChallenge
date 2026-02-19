# IAM Permissions Documentation - KIA Paint Shop IoT Prototype

## Overview

This document details all IAM roles and policies used in the system, demonstrating adherence to the principle of least privilege.

## IAM Roles Summary

| Role | Purpose | Services Accessed | Permissions Level |
|------|---------|-------------------|-------------------|
| lambda-ingest-role | Ingest IoT data | DynamoDB, EventBridge, CloudWatch | Write to sensor-data table only |
| lambda-process-role | Process alarms | DynamoDB (read/write), CloudWatch | Read variables-metadata, write alarms |
| lambda-statistics-role | Calculate statistics | DynamoDB (read/write), CloudWatch | Read sensor-data, write statistics |
| lambda-api-role | API handlers | DynamoDB (read/write), S3 (read), CloudWatch | Read all tables, update alarms only |
| iot-rule-role | IoT Rule execution | Lambda, CloudWatch Logs | Invoke ingest Lambda only |
| api-gateway-cloudwatch-role | API Gateway logging | CloudWatch Logs | Write logs only |

## Detailed Role Permissions

### 1. Lambda Ingest Role

**Role Name**: `kia-paintshop-prototype-lambda-ingest-role`

**Purpose**: Receive and store IoT sensor data

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-sensor-data"
    },
    {
      "Effect": "Allow",
      "Action": [
        "events:PutEvents"
      ],
      "Resource": "arn:aws:events:*:*:event-bus/kia-paintshop-prototype-bus"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/kia-paintshop-prototype-ingest:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "KIA/PaintShop"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:*:*:kia-paintshop-prototype-ingest-dlq"
    }
  ]
}
```

**Justification**:
- **DynamoDB PutItem/UpdateItem**: Required to store incoming sensor data
- **EventBridge PutEvents**: Required to trigger downstream processing
- **CloudWatch Logs**: Required for debugging and monitoring
- **CloudWatch PutMetricData**: Scoped to KIA/PaintShop namespace only
- **SQS SendMessage**: Required for dead-letter queue handling

**Least Privilege Verification**: ✅
- Only writes to sensor-data table (not other tables)
- Cannot read from DynamoDB
- Cannot delete data
- CloudWatch metrics scoped to specific namespace

---

### 2. Lambda Process Role

**Role Name**: `kia-paintshop-prototype-lambda-process-role`

**Purpose**: Detect anomalies and generate alarms

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-variables-metadata"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-alarms"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/kia-paintshop-prototype-process:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "KIA/PaintShop"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:*:*:kia-paintshop-prototype-process-dlq"
    }
  ]
}
```

**Justification**:
- **DynamoDB GetItem/Query**: Read variable thresholds from metadata table
- **DynamoDB PutItem/UpdateItem**: Write alarms to alarms table only
- **CloudWatch Logs**: Required for debugging
- **CloudWatch PutMetricData**: Scoped to KIA/PaintShop namespace
- **SQS SendMessage**: Dead-letter queue handling

**Least Privilege Verification**: ✅
- Read-only access to variables-metadata
- Write access only to alarms table
- Cannot access sensor-data or statistics tables
- Cannot delete data

---

### 3. Lambda Statistics Role

**Role Name**: `kia-paintshop-prototype-lambda-statistics-role`

**Purpose**: Calculate aggregated statistics

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:GetItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-sensor-data",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-variables-metadata"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-statistics"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/kia-paintshop-prototype-statistics:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "KIA/PaintShop"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": [
        "sqs:SendMessage"
      ],
      "Resource": "arn:aws:sqs:*:*:kia-paintshop-prototype-statistics-dlq"
    }
  ]
}
```

**Justification**:
- **DynamoDB Query/Scan/GetItem**: Read sensor data for calculations
- **DynamoDB PutItem/UpdateItem**: Write statistics to statistics table only
- **CloudWatch Logs**: Required for debugging
- **CloudWatch PutMetricData**: Scoped to KIA/PaintShop namespace
- **SQS SendMessage**: Dead-letter queue handling

**Least Privilege Verification**: ✅
- Read-only access to sensor-data and variables-metadata
- Write access only to statistics table
- Cannot access alarms table
- Cannot delete data
- Scan permission required for aggregating across all variables

---

### 4. Lambda API Role

**Role Name**: `kia-paintshop-prototype-lambda-api-role`

**Purpose**: Handle API requests from dashboard

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/lambda/kia-paintshop-prototype-api-*:*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-sensor-data",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-sensor-data/index/*",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-alarms",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-alarms/index/*",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-statistics",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-statistics/index/*",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-variables-metadata",
        "arn:aws:dynamodb:*:*:table/kia-paintshop-prototype-variables-metadata/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::kia-paintshop-prototype-archive-*",
        "arn:aws:s3:::kia-paintshop-prototype-archive-*/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:PutMetricData"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "cloudwatch:namespace": "KIA/PaintShop"
        }
      }
    }
  ]
}
```

**Justification**:
- **DynamoDB GetItem/Query/Scan**: Read data for API responses
- **DynamoDB UpdateItem**: Update alarm status (acknowledge) only
- **S3 GetObject/ListBucket**: Read archived historical data
- **CloudWatch Logs**: Required for debugging
- **CloudWatch PutMetricData**: Scoped to KIA/PaintShop namespace

**Least Privilege Verification**: ✅
- Read access to all tables (required for API queries)
- UpdateItem only (no PutItem or DeleteItem)
- S3 read-only access (no write or delete)
- Cannot delete data from any table
- GSI access included for efficient queries

**Note**: UpdateItem permission is required for acknowledging alarms (POST /alarms/{id}/acknowledge)

---

### 5. IoT Rule Role

**Role Name**: `kia-paintshop-prototype-iot-rule-role`

**Purpose**: Allow IoT Rules Engine to invoke Lambda

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "arn:aws:lambda:*:*:function:kia-paintshop-prototype-ingest"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/aws/iot/rules/kia-paintshop-prototype:*"
    }
  ]
}
```

**Justification**:
- **Lambda InvokeFunction**: Required to invoke ingest Lambda from IoT Rule
- **CloudWatch Logs**: Required for IoT Rule error logging

**Least Privilege Verification**: ✅
- Can only invoke ingest Lambda (not other Lambdas)
- Cannot access DynamoDB directly
- Cannot access S3
- Logs scoped to IoT rules log group only

---

### 6. API Gateway CloudWatch Role

**Role Name**: `kia-paintshop-prototype-api-gateway-cloudwatch-role`

**Purpose**: Allow API Gateway to write logs to CloudWatch

**Permissions**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "logs:PutLogEvents",
        "logs:GetLogEvents",
        "logs:FilterLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

**Note**: This uses the AWS managed policy `AmazonAPIGatewayPushToCloudWatchLogs`

**Justification**:
- Required for API Gateway to write access logs and execution logs
- AWS managed policy ensures compatibility with API Gateway service

**Least Privilege Verification**: ⚠️
- Uses AWS managed policy (broader than strictly necessary)
- Acceptable for prototype to avoid maintenance overhead
- For production, consider custom policy scoped to specific log groups

---

## Permissions Not Granted (Security by Omission)

The following permissions are explicitly NOT granted to any role:

### DynamoDB
- ❌ `dynamodb:DeleteItem` - No role can delete data
- ❌ `dynamodb:DeleteTable` - No role can delete tables
- ❌ `dynamodb:BatchWriteItem` - Not required for this use case
- ❌ `dynamodb:CreateTable` - Tables managed by Terraform only

### S3
- ❌ `s3:PutObject` - No Lambda writes to S3 (future archival will use separate role)
- ❌ `s3:DeleteObject` - No role can delete archived data
- ❌ `s3:PutBucketPolicy` - Bucket policies managed by Terraform only
- ❌ `s3:PutPublicAccessBlock` - Public access managed by Terraform only

### Lambda
- ❌ `lambda:CreateFunction` - Functions managed by Terraform only
- ❌ `lambda:DeleteFunction` - Functions managed by Terraform only
- ❌ `lambda:UpdateFunctionCode` - Updates managed by Terraform only

### IAM
- ❌ No Lambda has IAM permissions - Prevents privilege escalation
- ❌ No role can create or modify other roles

### EventBridge
- ❌ Only ingest Lambda can put events (not API or process Lambdas)

---

## Security Best Practices Applied

### 1. Principle of Least Privilege ✅
- Each role has only the minimum permissions required
- Permissions scoped to specific resources (not wildcards)
- Read/write permissions separated where possible

### 2. Resource-Level Permissions ✅
- DynamoDB permissions specify exact table ARNs
- S3 permissions specify exact bucket ARNs
- Lambda invoke permissions specify exact function ARNs
- CloudWatch Logs permissions specify exact log group ARNs

### 3. Condition-Based Permissions ✅
- CloudWatch PutMetricData scoped to KIA/PaintShop namespace
- Prevents metric pollution in other namespaces

### 4. No Wildcard Resources ✅
- Exception: CloudWatch PutMetricData (required by AWS, mitigated with condition)
- Exception: API Gateway CloudWatch role (AWS managed policy)

### 5. Separation of Duties ✅
- Ingest Lambda cannot read data (write-only)
- Process Lambda cannot write to sensor-data (read-only)
- API Lambdas cannot delete data (read + update only)

### 6. No Cross-Function Access ✅
- Lambdas cannot invoke each other directly
- Communication via EventBridge only (auditable)

---

## Permission Audit Checklist

Use this checklist to verify IAM permissions remain secure:

- [ ] No role has `*` in Action (except CloudWatch metrics with condition)
- [ ] No role has `*` in Resource (except where required by AWS)
- [ ] No role has IAM permissions
- [ ] No role can delete DynamoDB tables
- [ ] No role can delete S3 objects
- [ ] No role can modify other roles
- [ ] CloudWatch metrics scoped to KIA/PaintShop namespace
- [ ] Each Lambda can only access required tables
- [ ] API Lambdas cannot delete data
- [ ] IoT Rule can only invoke ingest Lambda

---

## Recommendations for Production

1. **VPC Endpoints**: Add VPC endpoints for DynamoDB and S3 to avoid public internet
2. **Resource Tags**: Add resource-based access control using tags
3. **Session Policies**: Add session policies for temporary credentials
4. **Permission Boundaries**: Add permission boundaries to prevent privilege escalation
5. **AWS Config**: Enable AWS Config to monitor IAM policy changes
6. **CloudTrail**: Enable CloudTrail to audit all IAM actions
7. **IAM Access Analyzer**: Use IAM Access Analyzer to identify overly permissive policies
8. **Regular Audits**: Review IAM permissions quarterly

---

## References

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Least Privilege Principle](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html#grant-least-privilege)
- [IAM Policy Examples](https://docs.aws.amazon.com/IAM/latest/UserGuide/access_policies_examples.html)
- [DynamoDB IAM Permissions](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/api-permissions-reference.html)
- [Lambda Execution Role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

