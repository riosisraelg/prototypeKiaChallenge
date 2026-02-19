#!/bin/bash

# KIA Paint Shop IoT Prototype - Setup Script
# This script automates the complete deployment of the IoT prototype

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="kia-paintshop-iot"
REGION="${AWS_REGION:-us-east-1}"
TERRAFORM_DIR="terraform"
SIMULATOR_DIR="simulator"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}KIA Paint Shop IoT Prototype - Setup${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v terraform &> /dev/null; then
    echo -e "${RED}Error: Terraform is not installed${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Check AWS credentials
echo -e "${YELLOW}Checking AWS credentials...${NC}"
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Run: aws configure"
    exit 1
fi

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo -e "${GREEN}✓ AWS Account: ${AWS_ACCOUNT_ID}${NC}"
echo ""

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
cd "$TERRAFORM_DIR"
terraform init
echo -e "${GREEN}✓ Terraform initialized${NC}"
echo ""

# Terraform plan
echo -e "${YELLOW}Running Terraform plan...${NC}"
terraform plan -out=tfplan
echo ""
read -p "Do you want to apply this plan? (yes/no): " APPLY_CONFIRM

if [ "$APPLY_CONFIRM" != "yes" ]; then
    echo -e "${YELLOW}Setup cancelled by user${NC}"
    exit 0
fi

# Apply Terraform
echo -e "${YELLOW}Applying Terraform configuration...${NC}"
terraform apply tfplan
echo -e "${GREEN}✓ Infrastructure deployed${NC}"
echo ""

# Get outputs
echo -e "${YELLOW}Retrieving deployment outputs...${NC}"
API_URL=$(terraform output -raw api_url 2>/dev/null || echo "")
API_KEY=$(terraform output -raw api_key 2>/dev/null || echo "")
IOT_ENDPOINT=$(terraform output -raw iot_endpoint 2>/dev/null || echo "")
IOT_THING_NAME=$(terraform output -raw iot_thing_name 2>/dev/null || echo "")

echo -e "${GREEN}✓ Outputs retrieved${NC}"
echo ""

# Save outputs to file
OUTPUTS_FILE="../.deployment_outputs"
cat > "$OUTPUTS_FILE" << EOF
API_URL=$API_URL
API_KEY=$API_KEY
IOT_ENDPOINT=$IOT_ENDPOINT
IOT_THING_NAME=$IOT_THING_NAME
REGION=$REGION
DEPLOYED_AT=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF

echo -e "${GREEN}✓ Outputs saved to $OUTPUTS_FILE${NC}"
echo ""

# Download IoT certificates
echo -e "${YELLOW}Downloading IoT certificates...${NC}"
CERT_DIR="../$SIMULATOR_DIR/certs"
mkdir -p "$CERT_DIR"

# Note: Certificates must be downloaded from AWS Console or created via AWS CLI
echo -e "${YELLOW}Note: IoT certificates must be downloaded manually from AWS Console${NC}"
echo "1. Go to AWS IoT Core Console"
echo "2. Navigate to Security > Certificates"
echo "3. Download certificate, private key, and root CA"
echo "4. Save them to: $CERT_DIR/"
echo ""

# Test API endpoints
echo -e "${YELLOW}Testing API endpoints...${NC}"
cd ..

if [ -n "$API_URL" ] && [ -n "$API_KEY" ]; then
    echo "Testing GET /variables..."
    RESPONSE=$(curl -s -w "\n%{http_code}" -H "x-api-key: $API_KEY" "$API_URL/variables")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✓ API is responding correctly${NC}"
    else
        echo -e "${YELLOW}⚠ API returned status code: $HTTP_CODE${NC}"
    fi
else
    echo -e "${YELLOW}⚠ API URL or Key not available, skipping API test${NC}"
fi
echo ""

# Display summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Deployment Information:${NC}"
echo "API URL: $API_URL"
echo "API Key: $API_KEY"
echo "IoT Endpoint: $IOT_ENDPOINT"
echo "IoT Thing: $IOT_THING_NAME"
echo "Region: $REGION"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Download IoT certificates to $CERT_DIR/"
echo "2. Configure simulator: cd $SIMULATOR_DIR && python simulator.py"
echo "3. Build dashboard: cd dashboard && npm install && npm run build"
echo "4. Monitor logs: aws logs tail /aws/lambda/kia-paintshop-ingest --follow"
echo ""
echo -e "${YELLOW}Outputs saved to: $OUTPUTS_FILE${NC}"
echo ""
echo -e "${GREEN}Estimated monthly cost: \$1-5${NC}"
echo ""
