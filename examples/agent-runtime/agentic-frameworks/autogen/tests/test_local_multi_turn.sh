#!/bin/bash

# Multi-turn conversation test
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash tests/test_local_multi_turn.sh

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
echo -e "${GREEN}🚀 AutoGen Agent Multi-turn Conversation Test${NC}"
echo "========================================================================"
echo ""

# Check service
if ! curl -s -f "${BASE_URL}/ping" > /dev/null 2>&1; then
    echo "❌ Service not running! Start with: python app.py"
    exit 1
fi

# Round 1
echo "========================================================================"
echo -e "${BLUE}Round 1${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 How's the weather in New York?${NC}"
echo ""

RESPONSE1=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "How is the weather in New York?", "streaming": false}')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE1}" | jq -r '.result // .error // .'
echo ""
sleep 1

# Round 2: Test memory
echo "========================================================================"
echo -e "${BLUE}Round 2: Testing Memory${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Which city's weather did I just ask about?${NC}"
echo ""

RESPONSE2=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Which city weather did I just ask about?", "streaming": false}')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE2}" | jq -r '.result // .error // .'
echo ""

# Check memory
if echo "${RESPONSE2}" | grep -qi "New York"; then
    echo -e "${GREEN}✅ Success! Agent remembered the previous conversation content!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Agent may not have remembered the previous conversation${NC}"
fi

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ Multi-turn conversation test completed${NC}"
echo "========================================================================"
echo ""
