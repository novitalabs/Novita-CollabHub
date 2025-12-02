#!/bin/bash

# Basic streaming test - Single-turn conversation
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash tests/test_local_streaming.sh

set -e  # Exit on error

# Service configuration
BASE_URL="http://localhost:8080"
ENDPOINT="${BASE_URL}/invocations"

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo "========================================================================"
echo -e "${GREEN}🚀 Streaming Test (Single-turn)${NC}"
echo "========================================================================"
echo ""

# Check if service is available
echo -e "${CYAN}📡 Checking service status...${NC}"
if curl -s -f "${BASE_URL}/ping" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Service is running${NC}"
    echo ""
else
    echo -e "${RED}❌ Service is not running! Please start it first: python app.py${NC}"
    exit 1
fi

# Streaming test
echo "========================================================================"
echo -e "${BLUE}🗣️  Streaming Test${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Sending: Tell me something interesting about AI Agents.${NC}"
echo ""
echo -e "${GREEN}📥 Streaming response:${NC}"

curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Tell me something interesting about AI Agents.",
        "streaming": true
    }' | while IFS= read -r line; do
        # Only display data: line content
        if [[ "$line" == data:* ]]; then
            echo "$line" | sed 's/^data: //' | jq -r '.chunk // .error // empty' | tr -d '\n'
        fi
    done

echo ""
echo ""

echo "========================================================================"
echo -e "${GREEN}✅ Streaming test completed successfully${NC}"
echo "========================================================================"
echo ""

