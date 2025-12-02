#!/bin/bash

# Multi-turn conversation test
# Usage: 
#   1. Start app.py: python app.py
#   2. Run this script: bash test_multi_turn_local.sh

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
echo -e "${GREEN}🚀 Multi-turn Conversation Test${NC}"
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

# Round 1
echo "========================================================================"
echo -e "${BLUE}🗣️  Round 1${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Sending: Hello, agent! My name is Jason.${NC}"
echo ""

RESPONSE1=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Hello, agent! My name is Jason.",
        "streaming": false
    }')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE1}" | jq -r '.result // .error // .'
echo ""
echo -e "${CYAN}⏳ Waiting 2 seconds before next round...${NC}"
sleep 2
echo ""

# Round 2
echo "========================================================================"
echo -e "${BLUE}🗣️  Round 2${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Sending: Tell me something interesting about AI Agents.${NC}"
echo ""

RESPONSE2=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "Tell me something interesting about AI Agents.",
        "streaming": false
    }')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE2}" | jq -r '.result // .error // .'
echo ""
echo -e "${CYAN}⏳ Waiting 2 seconds before next round...${NC}"
sleep 2
echo ""

# Round 3 - Test memory capability
echo "========================================================================"
echo -e "${BLUE}🗣️  Round 3 (Testing Memory)${NC}"
echo "========================================================================"
echo -e "${YELLOW}📤 Sending: What's my name? Can you remember it?${NC}"
echo ""

RESPONSE3=$(curl -s -X POST "${ENDPOINT}" \
    -H "Content-Type: application/json" \
    -d '{
        "prompt": "What'\''s my name? Can you remember it?",
        "streaming": false
    }')

echo -e "${GREEN}📥 Response:${NC}"
echo "${RESPONSE3}" | jq -r '.result // .error // .'
echo ""

# Check if name is remembered
if echo "${RESPONSE3}" | grep -qi "jason"; then
    echo -e "${GREEN}✅ Success! Agent remembered your name!${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Agent may not have remembered your name${NC}"
fi

echo ""
echo "========================================================================"
echo -e "${GREEN}✅ Multi-turn conversation test completed${NC}"
echo "========================================================================"
echo ""

