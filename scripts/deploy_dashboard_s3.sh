#!/bin/bash
# KIA Paint Shop IoT Prototype - Dashboard S3 Deployment Script
# Alternative deployment: Deploy React dashboard to S3 (simpler than Amplify)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== KIA Paint Shop Dashboard S3 Deployment ===${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}Error: npm is not installed${NC}"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All prerequisites met${NC}"
echo ""

# Get Terraform outputs
echo -e "${YELLOW}Retrieving Terraform outputs...${NC}"

cd "$(dirname "$0")/../terraform"

if [ ! -f "terraform.tfstate" ]; then
    echo -e "${RED}Error: Terraform state not found. Run 'terraform apply' first.${NC}"
    exit 1
fi

API_URL=$(terraform output -raw api_url 2>/dev/null || echo "")
API_KEY=$(terraform output -raw api_key 2>/dev/null || echo "")
AWS_REGION=$(terraform output -raw aws_region 2>/dev/null || echo "us-east-1")
AWS_ACCOUNT_ID=$(terraform output -raw aws_account_id 2>/dev/null || echo "")

if [ -z "$API_URL" ] || [ -z "$API_KEY" ]; then
    echo -e "${RED}Error: Required Terraform outputs not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Retrieved Terraform outputs${NC}"
echo ""

# Navigate to dashboard directory
cd ../dashboard

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm ci --silent
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create .env.production file
echo -e "${YELLOW}Configuring environment variables...${NC}"
cat > .env.production <<EOF
REACT_APP_API_URL=$API_URL
REACT_APP_API_KEY=$API_KEY
GENERATE_SOURCEMAP=false
EOF

echo -e "${GREEN}✓ Environment configured${NC}"
echo ""

# Build the React app
echo -e "${YELLOW}Building React application...${NC}"
npm run build
echo -e "${GREEN}✓ Build completed${NC}"
echo ""

# Create S3 bucket for dashboard hosting
DASHBOARD_BUCKET="kia-paintshop-dashboard-${AWS_ACCOUNT_ID}"

echo -e "${YELLOW}Setting up S3 bucket for hosting...${NC}"

# Check if bucket exists
if aws s3 ls "s3://${DASHBOARD_BUCKET}" 2>/dev/null; then
    echo "Bucket already exists: ${DASHBOARD_BUCKET}"
else
    echo "Creating bucket: ${DASHBOARD_BUCKET}"
    aws s3 mb "s3://${DASHBOARD_BUCKET}" --region "$AWS_REGION"
fi

# Configure bucket for static website hosting
aws s3 website "s3://${DASHBOARD_BUCKET}" \
    --index-document index.html \
    --error-document index.html

# Set bucket policy for public read access
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${DASHBOARD_BUCKET}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$DASHBOARD_BUCKET" \
    --policy file:///tmp/bucket-policy.json

rm /tmp/bucket-policy.json

# Disable block public access (required for website hosting)
aws s3api put-public-access-block \
    --bucket "$DASHBOARD_BUCKET" \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

echo -e "${GREEN}✓ S3 bucket configured for hosting${NC}"
echo ""

# Upload build to S3
echo -e "${YELLOW}Uploading dashboard to S3...${NC}"
aws s3 sync build/ "s3://${DASHBOARD_BUCKET}/" \
    --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html" \
    --quiet

# Upload index.html separately with no-cache
aws s3 cp build/index.html "s3://${DASHBOARD_BUCKET}/index.html" \
    --cache-control "no-cache, no-store, must-revalidate" \
    --content-type "text/html" \
    --quiet

echo -e "${GREEN}✓ Dashboard uploaded to S3${NC}"
echo ""

# Get website URL
WEBSITE_URL="http://${DASHBOARD_BUCKET}.s3-website-${AWS_REGION}.amazonaws.com"

echo -e "${BLUE}=== Deployment Complete ===${NC}"
echo ""
echo -e "${GREEN}Dashboard URL: ${WEBSITE_URL}${NC}"
echo ""
echo -e "${YELLOW}Note:${NC} This is an HTTP endpoint. For HTTPS, consider:"
echo "  1. Setting up CloudFront distribution"
echo "  2. Using AWS Amplify (run deploy_dashboard.sh)"
echo "  3. Adding a custom domain with SSL certificate"
echo ""
echo -e "${YELLOW}Cost:${NC} S3 hosting is very cheap (~\$0.50/month for this use case)"
echo ""
echo -e "${GREEN}Deployment successful!${NC}"
