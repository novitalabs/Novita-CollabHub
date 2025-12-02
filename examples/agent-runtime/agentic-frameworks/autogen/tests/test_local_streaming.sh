#!/bin/bash

# Streaming test
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash tests/test_local_streaming.sh

set -e

# Service configuration
BASE_URL="http://localhost:8080"
ENDPOINT="${BASE_URL}/invocations"

# Color output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================================================"
echo -e "${GREEN}🚀 AutoGen Agent Streaming Output Test${NC}"
echo "========================================================================"
echo ""

# Check service
if ! curl -s -f "${BASE_URL}/ping" > /dev/null 2>&1; then
    echo "❌ Service not running! Start with: python app.py"
    exit 1
fi

# Streaming test
echo "========================================================================"
echo -e "${BLUE}Streaming Output Test${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Query the weather in New York and calculate 25 + 15${NC}"
echo -e "${GREEN}📥 Streaming response:${NC}"

curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Query the weather in New York and calculate 25 + 15", "streaming": true}' | \
    while IFS= read -r line; do
        if [[ "$line" == data:* ]]; then
            echo "$line" | sed 's/^data: //' | jq -r '.chunk // .error // empty' | tr -d '\n'
        fi
    done

echo ""
echo ""

echo "========================================================================"
echo -e "${GREEN}✅ Streaming test completed${NC}"
echo "========================================================================"
echo ""
