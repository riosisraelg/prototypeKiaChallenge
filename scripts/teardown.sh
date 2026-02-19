#!/bin/bash

# KIA Paint Shop IoT Prototype - Teardown Script
# This script safely destroys all AWS resources and cleans up local files

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

TERRAFORM_DIR="terraform"

echo -e "${RED}========================================${NC}"
echo -e "${RED}KIA Paint Shop IoT Prototype - Teardown${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "${YELLOW}WARNING: This will destroy ALL AWS resources!${NC}"
echo ""

# Confirm destruction
read -p "Are you sure you want to destroy all resources? Type 'yes' to confirm: " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${GREEN}Teardown cancelled${NC}"
    exit 0
fi

echo ""
read -p "Type the project name 'kia-paintshop-iot' to confirm: " PROJECT_CONFIRM

if [ "$PROJECT_CONFIRM" != "kia-paintshop-iot" ]; then
    echo -e "${RED}Project name mismatch. Teardown cancelled${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}Starting teardown process...${NC}"
echo ""

# Stop any running simulators
echo -e "${YELLOW}Checking for running simulator processes...${NC}"
if pgrep -f "simulator.py" > /dev/null; then
    echo "Stopping simulator..."
    pkill -f "simulator.py" || true
    echo -e "${GREEN}✓ Simulator stopped${NC}"
else
    echo -e "${GREEN}✓ No simulator running${NC}"
fi
echo ""

# Empty S3 buckets before destruction
echo -e "${YELLOW}Emptying S3 buckets...${NC}"
cd "$TERRAFORM_DIR"

# Get bucket name from Terraform state
BUCKET_NAME=$(terraform output -raw s3_bucket_name 2>/dev/null || echo "")

if [ -n "$BUCKET_NAME" ]; then
    echo "Emptying bucket: $BUCKET_NAME"
    aws s3 rm "s3://$BUCKET_NAME" --recursive 2>/dev/null || true
    echo -e "${GREEN}✓ S3 bucket emptied${NC}"
else
    echo -e "${YELLOW}⚠ Could not find S3 bucket name${NC}"
fi
echo ""

# Destroy Terraform resources
echo -e "${YELLOW}Destroying Terraform resources...${NC}"
terraform destroy -auto-approve

echo -e "${GREEN}✓ All Terraform resources destroyed${NC}"
echo ""

# Clean up local files
echo -e "${YELLOW}Cleaning up local files...${NC}"
cd ..

# Remove deployment outputs
if [ -f ".deployment_outputs" ]; then
    rm .deployment_outputs
    echo -e "${GREEN}✓ Removed deployment outputs${NC}"
fi

# Remove Terraform state backups
rm -f "$TERRAFORM_DIR/terraform.tfstate.backup"
rm -f "$TERRAFORM_DIR/tfplan"
echo -e "${GREEN}✓ Removed Terraform artifacts${NC}"

# Optional: Remove IoT certificates
read -p "Do you want to remove IoT certificates? (yes/no): " REMOVE_CERTS
if [ "$REMOVE_CERTS" = "yes" ]; then
    rm -rf simulator/certs/*
    echo -e "${GREEN}✓ Removed IoT certificates${NC}"
fi

echo ""

# Verify cleanup
echo -e "${YELLOW}Running cleanup verification...${NC}"
./scripts/verify_cleanup.sh

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Teardown Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}All AWS resources have been destroyed${NC}"
echo -e "${YELLOW}Local artifacts have been cleaned up${NC}"
echo ""
echo -e "${GREEN}You can now safely delete this project directory${NC}"
echo ""
