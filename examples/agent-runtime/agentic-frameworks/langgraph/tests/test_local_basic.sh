#!/bin/bash

# Basic functionality test - Non-streaming
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash tests/test_local_basic.sh

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
echo -e "${GREEN}🚀 Basic Functionality Test (Non-Streaming)${NC}"
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

# Basic test
echo "========================================================================"
echo -e "${BLUE}🗣️  Basic Test${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Sending: Hello, Agent! Tell me something interesting about AI Agents.${NC}"
echo ""

RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Hello, Agent! Tell me something interesting about AI Agents.",
        "streaming": false
    }')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result // .error // .'
echo ""

# Check if response is valid
if echo "${RESPONSE}" | jq -e '.result' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Success! Agent responded correctly.${NC}"
else
    echo -e "${RED}❌ Error: Invalid response format${NC}"
    exit 1
fi

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ Basic test completed successfully${NC}"
echo "========================================================================"
echo ""

