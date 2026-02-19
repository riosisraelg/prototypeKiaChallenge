#!/bin/bash

# Quick Dashboard Test Script
# This script helps you quickly test the dashboard by checking prerequisites
# and providing step-by-step guidance

set -e

echo "=========================================="
echo "KIA Paint Shop Dashboard - Quick Test"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
    else
        echo -e "${RED}✗${NC} $2"
    fi
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print info
print_info() {
    echo -e "${GREEN}ℹ${NC} $1"
}

echo "Step 1: Checking Prerequisites"
echo "--------------------------------"

# Check if terraform is installed
if command -v terraform &> /dev/null; then
    print_status 0 "Terraform installed"
else
    print_status 1 "Terraform not installed"
    echo "  Install from: https://www.terraform.io/downloads"
    exit 1
fi

# Check if node/npm is installed
if command -v npm &> /dev/null; then
    print_status 0 "Node.js/npm installed"
else
    print_status 1 "Node.js/npm not installed"
    echo "  Install from: https://nodejs.org/"
    exit 1
fi

# Check if python3 is installed
if command -v python3 &> /dev/null; then
    print_status 0 "Python 3 installed"
else
    print_status 1 "Python 3 not installed"
    exit 1
fi

echo ""
echo "Step 2: Checking Infrastructure Status"
echo "---------------------------------------"

cd terraform

# Check if terraform is initialized
if [ -d ".terraform" ]; then
    print_status 0 "Terraform initialized"
else
    print_status 1 "Terraform not initialized"
    print_info "Run: cd terraform && terraform init"
    exit 1
fi

# Check if infrastructure is deployed
if terraform show -json 2>/dev/null | grep -q "values"; then
    print_status 0 "Infrastructure deployed"
    
    # Get outputs
    echo ""
    echo "Step 3: Getting Configuration Values"
    echo "-------------------------------------"
    
    API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
    API_KEY=$(terraform output -raw api_key 2>/dev/null || echo "")
    IOT_ENDPOINT=$(terraform output -raw iot_endpoint 2>/dev/null || echo "")
    
    if [ -n "$API_URL" ]; then
        print_status 0 "API Gateway URL: $API_URL"
    else
        print_warning "Could not get API Gateway URL"
    fi
    
    if [ -n "$API_KEY" ]; then
        print_status 0 "API Key: ${API_KEY:0:20}..."
    else
        print_warning "Could not get API Key"
    fi
    
    if [ -n "$IOT_ENDPOINT" ]; then
        print_status 0 "IoT Endpoint: $IOT_ENDPOINT"
    else
        print_warning "Could not get IoT Endpoint"
    fi
    
else
    print_status 1 "Infrastructure not deployed"
    echo ""
    print_info "To deploy infrastructure:"
    echo "  cd terraform"
    echo "  terraform plan"
    echo "  terraform apply"
    echo ""
    read -p "Would you like to deploy now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deploying infrastructure..."
        terraform apply -auto-approve
        
        # Get outputs after deployment
        API_URL=$(terraform output -raw api_gateway_url 2>/dev/null || echo "")
        API_KEY=$(terraform output -raw api_key 2>/dev/null || echo "")
        IOT_ENDPOINT=$(terraform output -raw iot_endpoint 2>/dev/null || echo "")
    else
        echo "Skipping deployment. Please deploy manually before testing dashboard."
        exit 1
    fi
fi

cd ..

echo ""
echo "Step 4: Configuring Dashboard"
echo "------------------------------"

cd dashboard

# Check if node_modules exists
if [ -d "node_modules" ]; then
    print_status 0 "Dashboard dependencies installed"
else
    print_status 1 "Dashboard dependencies not installed"
    print_info "Installing dependencies..."
    npm install
fi

# Check if .env.local exists
if [ -f ".env.local" ]; then
    print_status 0 ".env.local exists"
else
    print_warning ".env.local not found, creating from template..."
    
    if [ -n "$API_URL" ] && [ -n "$API_KEY" ]; then
        cat > .env.local << EOF
# API Configuration
REACT_APP_API_URL=$API_URL
REACT_APP_API_KEY=$API_KEY
EOF
        print_status 0 "Created .env.local with API configuration"
    else
        cp .env.example .env.local
        print_warning "Created .env.local from template - please edit with your values"
        echo "  Edit: dashboard/.env.local"
    fi
fi

cd ..

echo ""
echo "Step 5: Checking Simulator Status"
echo "----------------------------------"

# Check if simulator is running
if pgrep -f "simulator.py" > /dev/null; then
    print_status 0 "Simulator is running"
else
    print_warning "Simulator is not running"
    print_info "To start simulator:"
    echo "  cd simulator"
    echo "  python3 simulator.py --config config.yaml"
    echo ""
    read -p "Would you like to start the simulator in background? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd simulator
        # Check if config.yaml has IoT endpoint configured
        if [ -n "$IOT_ENDPOINT" ]; then
            # Update config.yaml with IoT endpoint if needed
            print_info "Starting simulator..."
            nohup python3 simulator.py --config config.yaml > simulator.log 2>&1 &
            print_status 0 "Simulator started (PID: $!)"
            print_info "Logs: simulator/simulator.log"
        else
            print_warning "IoT endpoint not available. Please configure simulator/config.yaml manually."
        fi
        cd ..
    fi
fi

echo ""
echo "=========================================="
echo "Ready to Test Dashboard!"
echo "=========================================="
echo ""
print_info "To start the dashboard:"
echo "  cd dashboard"
echo "  npm start"
echo ""
print_info "The dashboard will open at: http://localhost:3000"
echo ""
print_info "Verification checklist:"
echo "  1. Dashboard loads without errors"
echo "  2. 100 variables display in organized list"
echo "  3. Click a variable to see chart"
echo "  4. Chart shows data and auto-refreshes"
echo "  5. Alarms appear in alarm panel (if any)"
echo "  6. Can acknowledge alarms"
echo "  7. Connection status shows 'Connected'"
echo ""
print_info "For detailed verification steps, see: DASHBOARD_VERIFICATION_GUIDE.md"
echo ""

read -p "Start dashboard now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    cd dashboard
    print_info "Starting dashboard... (Press Ctrl+C to stop)"
    npm start
fi
