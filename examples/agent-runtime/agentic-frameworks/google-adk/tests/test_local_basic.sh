#!/bin/bash

set -e

BASE_URL="http://localhost:8080"
ENDPOINT="${BASE_URL}/invocations"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "========================================================================"
echo -e "${GREEN}🚀 Google ADK Agent Tests${NC}"
echo "========================================================================"
echo ""

if ! curl -s -f "${BASE_URL}/ping" > /dev/null 2>&1; then
    echo "❌ Service not running! Start with: python app.py"
    exit 1
fi

# Test 1
echo "========================================================================"
echo -e "${BLUE}Test 1: Simple Query${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 What is an AI Agent?${NC}"
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is an AI Agent?"}')
echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result // .error // .'
echo ""

# Test 2
echo "========================================================================"
echo -e "${BLUE}Test 2: Google Search${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 What's the latest AI news?${NC}"
RESPONSE=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is the latest AI news?"}')
echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE}" | jq -r '.result // .error // .'
echo ""

echo "========================================================================"
echo -e "${GREEN}✅ All tests completed${NC}"
echo "========================================================================"
echo ""
