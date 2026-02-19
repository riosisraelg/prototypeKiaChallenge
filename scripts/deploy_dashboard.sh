#!/bin/bash
# KIA Paint Shop IoT Prototype - Dashboard Deployment Script
# Task 14.2: Build and deploy React dashboard to AWS Amplify

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== KIA Paint Shop Dashboard Deployment ===${NC}"
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

if ! command -v jq &> /dev/null; then
    echo -e "${RED}Error: jq is not installed (required for JSON parsing)${NC}"
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

# Export outputs to JSON
terraform output -json > ../outputs.json

API_URL=$(terraform output -raw api_url 2>/dev/null || echo "")
API_KEY=$(terraform output -raw api_key 2>/dev/null || echo "")
AMPLIFY_APP_ID=$(terraform output -raw amplify_app_id 2>/dev/null || echo "")

if [ -z "$API_URL" ] || [ -z "$API_KEY" ] || [ -z "$AMPLIFY_APP_ID" ]; then
    echo -e "${RED}Error: Required Terraform outputs not found${NC}"
    echo "Make sure Terraform has been applied with Amplify configuration"
    exit 1
fi

echo -e "${GREEN}✓ Retrieved Terraform outputs${NC}"
echo "  API URL: $API_URL"
echo "  Amplify App ID: $AMPLIFY_APP_ID"
echo ""

# Navigate to dashboard directory
cd ../dashboard

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
npm ci --silent
echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# Create .env.production file with API configuration
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

# Create deployment package
echo -e "${YELLOW}Creating deployment package...${NC}"
cd build
zip -r ../dashboard-build.zip . -q
cd ..
echo -e "${GREEN}✓ Deployment package created${NC}"
echo ""

# Deploy to Amplify
echo -e "${YELLOW}Deploying to AWS Amplify...${NC}"

# Create a deployment using Amplify CLI or AWS CLI
# Note: Amplify doesn't have direct CLI deployment for manual builds
# We'll use a workaround by uploading to S3 and triggering Amplify

# Get AWS account ID and region
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region || echo "us-east-1")

# Create temporary S3 bucket for deployment artifacts (if needed)
DEPLOY_BUCKET="kia-paintshop-dashboard-deploy-${AWS_ACCOUNT_ID}"

# Check if bucket exists, create if not
if ! aws s3 ls "s3://${DEPLOY_BUCKET}" 2>/dev/null; then
    echo "Creating deployment bucket..."
    aws s3 mb "s3://${DEPLOY_BUCKET}" --region "$AWS_REGION"
    
    # Add lifecycle policy to auto-delete old artifacts after 7 days
    cat > /tmp/lifecycle-policy.json <<EOF
{
  "Rules": [
    {
      "Id": "DeleteOldArtifacts",
      "Status": "Enabled",
      "Prefix": "",
      "Expiration": {
        "Days": 7
      }
    }
  ]
}
EOF
    aws s3api put-bucket-lifecycle-configuration \
        --bucket "$DEPLOY_BUCKET" \
        --lifecycle-configuration file:///tmp/lifecycle-policy.json
    rm /tmp/lifecycle-policy.json
fi

# Upload build to S3
echo "Uploading build artifacts to S3..."
aws s3 sync build/ "s3://${DEPLOY_BUCKET}/builds/$(date +%Y%m%d-%H%M%S)/" --delete --quiet

echo -e "${GREEN}✓ Build artifacts uploaded${NC}"
echo ""

# For manual Amplify deployment, we need to use the Amplify Console
# or connect to a Git repository. Provide instructions:

echo -e "${BLUE}=== Deployment Options ===${NC}"
echo ""
echo -e "${YELLOW}Option 1: Manual Deployment via Amplify Console${NC}"
echo "1. Open AWS Amplify Console:"
echo "   https://console.aws.amazon.com/amplify/home?region=${AWS_REGION}#/${AMPLIFY_APP_ID}"
echo "2. Click on 'main' branch"
echo "3. Click 'Deploy without Git provider'"
echo "4. Upload the dashboard-build.zip file"
echo ""

echo -e "${YELLOW}Option 2: Deploy via S3 + CloudFront (Alternative)${NC}"
echo "The build artifacts are available at:"
echo "  s3://${DEPLOY_BUCKET}/builds/"
echo ""
echo "You can also deploy to S3 + CloudFront for hosting:"
echo "  ./scripts/deploy_dashboard_s3.sh"
echo ""

echo -e "${YELLOW}Option 3: Connect to Git Repository${NC}"
echo "1. Push your code to a Git repository (GitHub, GitLab, Bitbucket)"
echo "2. Connect Amplify app to your repository in AWS Console"
echo "3. Amplify will automatically build and deploy on push"
echo ""

# Display Amplify app URL
AMPLIFY_URL=$(cd ../terraform && terraform output -raw amplify_app_url 2>/dev/null || echo "")
if [ -n "$AMPLIFY_URL" ]; then
    echo -e "${GREEN}Dashboard URL (after deployment): ${AMPLIFY_URL}${NC}"
fi

echo ""
echo -e "${BLUE}=== Deployment Summary ===${NC}"
echo "✓ Build completed successfully"
echo "✓ Deployment package created: dashboard-build.zip"
echo "✓ Build artifacts uploaded to S3"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Choose a deployment option above"
echo "2. Complete the deployment"
echo "3. Access your dashboard at the Amplify URL"
echo ""
echo -e "${GREEN}Deployment preparation complete!${NC}"
