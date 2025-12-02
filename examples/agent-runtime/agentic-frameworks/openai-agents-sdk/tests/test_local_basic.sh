#!/bin/bash

# Basic functionality test - Non-streaming
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash tests/test_local_basic.sh

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
echo -e "${GREEN}🚀 AutoGen Agent Functionality Test${NC}"
echo "========================================================================"
echo ""

# Check service
if ! curl -s -f "${BASE_URL}/ping" > /dev/null 2>&1; then
    echo "❌ Service not running! Start with: python app.py"
    exit 1
fi

# Test 1: Weather Tool
echo "========================================================================"
echo -e "${BLUE}Test 1: Weather Query Tool (get_weather)${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Query the weather in New York${NC}"
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Query the weather in New York", "streaming": false}')
echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result'
echo ""

# Test 2: Search Tool
echo "========================================================================"
echo -e "${BLUE}Test 2: Information Search Tool (search_information)${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Search for AI-related information${NC}"
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Search for AI-related information", "streaming": false}')
echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result'
echo ""

# Test 3: Calculate Tool
echo "========================================================================"
echo -e "${BLUE}Test 3: Calculate Tool (calculate)${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Calculate 123 + 456${NC}"
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Calculate 123 + 456", "streaming": false}')
echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result'
echo ""

echo "========================================================================"
echo -e "${GREEN}✅ All tests completed${NC}"
echo "========================================================================"
echo ""
