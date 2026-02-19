#!/bin/bash

# KIA Paint Shop IoT Prototype - Cleanup Verification Script
# Verifies that all AWS resources have been properly deleted

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_PREFIX="kia-paintshop"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Cleanup Verification${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Checking for remaining AWS resources...${NC}"
echo -e "${YELLOW}Region: $REGION${NC}"
echo ""

ISSUES_FOUND=0

# Check S3 buckets
echo -e "${BLUE}Checking S3 buckets...${NC}"
S3_BUCKETS=$(aws s3api list-buckets --query "Buckets[?contains(Name, '$PROJECT_PREFIX')].Name" --output text 2>/dev/null || echo "")

if [ -n "$S3_BUCKETS" ]; then
    echo -e "${RED}✗ Found S3 buckets:${NC}"
    echo "$S3_BUCKETS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No S3 buckets found${NC}"
fi
echo ""

# Check DynamoDB tables
echo -e "${BLUE}Checking DynamoDB tables...${NC}"
DYNAMODB_TABLES=$(aws dynamodb list-tables --region "$REGION" --query "TableNames[?contains(@, '$PROJECT_PREFIX')]" --output text 2>/dev/null || echo "")

if [ -n "$DYNAMODB_TABLES" ]; then
    echo -e "${RED}✗ Found DynamoDB tables:${NC}"
    echo "$DYNAMODB_TABLES" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No DynamoDB tables found${NC}"
fi
echo ""

# Check Lambda functions
echo -e "${BLUE}Checking Lambda functions...${NC}"
LAMBDA_FUNCTIONS=$(aws lambda list-functions --region "$REGION" --query "Functions[?contains(FunctionName, '$PROJECT_PREFIX')].FunctionName" --output text 2>/dev/null || echo "")

if [ -n "$LAMBDA_FUNCTIONS" ]; then
    echo -e "${RED}✗ Found Lambda functions:${NC}"
    echo "$LAMBDA_FUNCTIONS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No Lambda functions found${NC}"
fi
echo ""

# Check IoT Things
echo -e "${BLUE}Checking IoT Things...${NC}"
IOT_THINGS=$(aws iot list-things --region "$REGION" --query "things[?contains(thingName, '$PROJECT_PREFIX')].thingName" --output text 2>/dev/null || echo "")

if [ -n "$IOT_THINGS" ]; then
    echo -e "${RED}✗ Found IoT Things:${NC}"
    echo "$IOT_THINGS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No IoT Things found${NC}"
fi
echo ""

# Check IoT Certificates
echo -e "${BLUE}Checking IoT Certificates...${NC}"
IOT_CERTS=$(aws iot list-certificates --region "$REGION" --query "certificates[?status=='ACTIVE'].certificateId" --output text 2>/dev/null || echo "")

if [ -n "$IOT_CERTS" ]; then
    CERT_COUNT=$(echo "$IOT_CERTS" | wc -w | tr -d ' ')
    echo -e "${YELLOW}⚠ Found $CERT_COUNT active IoT certificate(s)${NC}"
    echo "  (These may be from other projects - verify manually)"
else
    echo -e "${GREEN}✓ No active IoT certificates found${NC}"
fi
echo ""

# Check CloudWatch Log Groups
echo -e "${BLUE}Checking CloudWatch Log Groups...${NC}"
LOG_GROUPS=$(aws logs describe-log-groups --region "$REGION" --query "logGroups[?contains(logGroupName, '$PROJECT_PREFIX')].logGroupName" --output text 2>/dev/null || echo "")

if [ -n "$LOG_GROUPS" ]; then
    echo -e "${RED}✗ Found CloudWatch Log Groups:${NC}"
    echo "$LOG_GROUPS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No CloudWatch Log Groups found${NC}"
fi
echo ""

# Check API Gateways
echo -e "${BLUE}Checking API Gateways...${NC}"
API_GATEWAYS=$(aws apigateway get-rest-apis --region "$REGION" --query "items[?contains(name, '$PROJECT_PREFIX')].name" --output text 2>/dev/null || echo "")

if [ -n "$API_GATEWAYS" ]; then
    echo -e "${RED}✗ Found API Gateways:${NC}"
    echo "$API_GATEWAYS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No API Gateways found${NC}"
fi
echo ""

# Check EventBridge Rules
echo -e "${BLUE}Checking EventBridge Rules...${NC}"
EVENT_RULES=$(aws events list-rules --region "$REGION" --query "Rules[?contains(Name, '$PROJECT_PREFIX')].Name" --output text 2>/dev/null || echo "")

if [ -n "$EVENT_RULES" ]; then
    echo -e "${RED}✗ Found EventBridge Rules:${NC}"
    echo "$EVENT_RULES" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No EventBridge Rules found${NC}"
fi
echo ""

# Check IAM Roles
echo -e "${BLUE}Checking IAM Roles...${NC}"
IAM_ROLES=$(aws iam list-roles --query "Roles[?contains(RoleName, '$PROJECT_PREFIX')].RoleName" --output text 2>/dev/null || echo "")

if [ -n "$IAM_ROLES" ]; then
    echo -e "${RED}✗ Found IAM Roles:${NC}"
    echo "$IAM_ROLES" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No IAM Roles found${NC}"
fi
echo ""

# Check SNS Topics
echo -e "${BLUE}Checking SNS Topics...${NC}"
SNS_TOPICS=$(aws sns list-topics --region "$REGION" --query "Topics[?contains(TopicArn, '$PROJECT_PREFIX')].TopicArn" --output text 2>/dev/null || echo "")

if [ -n "$SNS_TOPICS" ]; then
    echo -e "${RED}✗ Found SNS Topics:${NC}"
    echo "$SNS_TOPICS" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No SNS Topics found${NC}"
fi
echo ""

# Check SQS Queues
echo -e "${BLUE}Checking SQS Queues...${NC}"
SQS_QUEUES=$(aws sqs list-queues --region "$REGION" --query "QueueUrls[?contains(@, '$PROJECT_PREFIX')]" --output text 2>/dev/null || echo "")

if [ -n "$SQS_QUEUES" ]; then
    echo -e "${RED}✗ Found SQS Queues:${NC}"
    echo "$SQS_QUEUES" | tr '\t' '\n' | sed 's/^/  - /'
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓ No SQS Queues found${NC}"
fi
echo ""

# Summary
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Verification Summary${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All resources cleaned up successfully!${NC}"
    echo -e "${GREEN}No remaining AWS resources found${NC}"
    echo ""
    echo -e "${GREEN}The project has been completely removed${NC}"
    echo -e "${GREEN}No residual charges will be incurred${NC}"
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES_FOUND resource type(s) still active${NC}"
    echo ""
    echo -e "${YELLOW}Recommended Actions:${NC}"
    echo "1. Review the resources listed above"
    echo "2. Manually delete any remaining resources via AWS Console"
    echo "3. Run 'terraform destroy' again if needed"
    echo "4. Check for resources in other regions"
    echo ""
    echo -e "${YELLOW}To manually clean up:${NC}"
    echo "  aws s3 rb s3://BUCKET_NAME --force"
    echo "  aws dynamodb delete-table --table-name TABLE_NAME"
    echo "  aws lambda delete-function --function-name FUNCTION_NAME"
    echo "  aws iot delete-thing --thing-name THING_NAME"
    echo ""
    exit 1
fi
