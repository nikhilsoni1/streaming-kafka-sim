#!/bin/bash
set -e

# Configuration
domain="ypr-dockyard"
repository="pypi-cargo"
format="pypi"

# Get the repository endpoint
endpoint=$(aws codeartifact get-repository-endpoint \
    --domain "$domain" \
    --repository "$repository" \
    --format "$format" \
    --query 'repositoryEndpoint' \
    --output text)

endpoint_stripped=$(echo "$endpoint" | sed -E 's#^https?://##')
endpoint_stripped_simple="${endpoint_stripped%/}/simple/"

# Get auth token
auth_token=$(aws codeartifact get-authorization-token \
    --domain "$domain" \
    --query authorizationToken \
    --output text)

# Build full authenticated index-url
auth_index_url="https://aws:${auth_token}@${endpoint_stripped_simple}"

# Configure pip
pip config set global.index-url "$auth_index_url"
pip config set global.extra-index-url "https://pypi.org/simple"
pip config set global.trusted-host "$endpoint_stripped"

echo "✅ Successfully configured pip:"
echo "Primary: $auth_index_url"
echo "Fallback: https://pypi.org/simple"
