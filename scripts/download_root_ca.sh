#!/bin/bash
# Download Amazon Root CA certificate for IoT Core TLS connection

set -e

CERTS_DIR="simulator/certs"
CA_FILE="$CERTS_DIR/AmazonRootCA1.pem"

echo "=== Downloading Amazon Root CA Certificate ==="

# Create certs directory if it doesn't exist
mkdir -p "$CERTS_DIR"

# Download Amazon Root CA 1
echo "Downloading AmazonRootCA1.pem..."
curl -o "$CA_FILE" https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Verify the file was downloaded
if [ -f "$CA_FILE" ]; then
  echo "✓ Certificate downloaded successfully to $CA_FILE"
  echo "✓ File size: $(wc -c < "$CA_FILE") bytes"
else
  echo "✗ Failed to download certificate"
  exit 1
fi

echo "=== Download Complete ==="
