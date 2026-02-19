#!/bin/bash
# Setup script for KIA Paint Shop IoT Simulator

set -e

echo "============================================================"
echo "KIA Paint Shop IoT Simulator - Setup"
echo "============================================================"
echo ""

# Check if terraform is deployed
echo "1. Checking Terraform deployment..."
cd terraform
if ! terraform output iot_endpoint &>/dev/null; then
    echo "❌ Terraform not deployed. Please run 'terraform apply' first."
    exit 1
fi

ENDPOINT=$(terraform output -raw iot_endpoint)
echo "✅ IoT endpoint: $ENDPOINT"
cd ..

# Check for certificates
echo ""
echo "2. Checking certificates..."
if [ ! -f "terraform/device.crt" ] || [ ! -f "terraform/device.key" ]; then
    echo "❌ Certificates not found in terraform/"
    echo "   Please ensure Terraform has created the certificates."
    exit 1
fi

# Copy certificates
echo "   Copying certificates to simulator/certs/..."
cp terraform/device.crt simulator/certs/
cp terraform/device.key simulator/certs/
chmod 600 simulator/certs/device.key
echo "✅ Certificates copied"

# Download Amazon Root CA
echo ""
echo "3. Downloading Amazon Root CA certificate..."
if [ ! -f "simulator/certs/AmazonRootCA1.pem" ]; then
    curl -s -o simulator/certs/AmazonRootCA1.pem \
        https://www.amazontrust.com/repository/AmazonRootCA1.pem
    echo "✅ Root CA downloaded"
else
    echo "✅ Root CA already exists"
fi

# Update config.yaml
echo ""
echo "4. Updating simulator configuration..."
if grep -q 'endpoint: ""' simulator/config.yaml; then
    sed -i.bak "s|endpoint: \"\"|endpoint: \"$ENDPOINT\"|" simulator/config.yaml
    echo "✅ Config updated with endpoint: $ENDPOINT"
else
    echo "✅ Config already has endpoint configured"
fi

# Verify Python dependencies
echo ""
echo "5. Checking Python dependencies..."
if ! python -c "import yaml" &>/dev/null; then
    echo "⚠️  PyYAML not installed. Installing..."
    pip install pyyaml
fi
if ! python -c "import paho.mqtt.client" &>/dev/null; then
    echo "⚠️  paho-mqtt not installed. Installing..."
    pip install paho-mqtt
fi
echo "✅ Python dependencies ready"

echo ""
echo "============================================================"
echo "Setup Complete!"
echo "============================================================"
echo ""
echo "To start the simulator:"
echo "  cd simulator"
echo "  python simulator.py"
echo ""
echo "To verify messages in AWS IoT Core:"
echo "  AWS Console → IoT Core → Test → Subscribe to 'kia/paintshop/#'"
echo ""
