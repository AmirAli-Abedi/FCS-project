#!/bin/bash
# Generate self-signed SSL certificate for local development
# This creates a certificate valid for 365 days

echo "Generating self-signed SSL certificate..."
echo "This certificate is for LOCAL DEVELOPMENT ONLY"
echo ""

mkdir -p ssl

openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem \
    -keyout ssl/key.pem \
    -days 365 \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

echo ""
echo "Certificate generated successfully!"
echo "Files created:"
echo "  - ssl/cert.pem (certificate)"
echo "  - ssl/key.pem (private key)"
echo ""
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "This is expected for local development. Click 'Advanced' and 'Proceed' to continue."

