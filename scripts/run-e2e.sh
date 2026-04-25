#!/usr/bin/env bash

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Change to project root
cd "${PROJECT_ROOT}"

echo -e "${YELLOW}Starting e2e test run locally...${NC}"

# Loading environment variables from Pulumi
echo -e "${YELLOW}Loading environment variables from Pulumi...${NC}"
# source the script directly to export variables to the current shell
if ! source "${PROJECT_ROOT}/scripts/load-env.sh"; then
    echo -e "${RED}Error: Failed to load environment from Pulumi. E2E tests require a valid local stack.${NC}"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    if [ -n "${API_PID:-}" ]; then
        kill "${API_PID}" 2>/dev/null || true
    fi
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Start API in the background
echo -e "${YELLOW}Starting API in background...${NC}"
uv run uvicorn src.main:app --port 8000 &
API_PID=$!

# Wait for API to be ready
echo -e "${YELLOW}Waiting for API to be ready...${NC}"
MAX_RETRIES=30
for ((i=1; i<=MAX_RETRIES; i++)); do
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}API is ready!${NC}"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo -e "${RED}API did not become ready in time${NC}"
        exit 1
    fi
    sleep 1
done

# Run pytest
echo -e "${YELLOW}Running tests...${NC}"
if uv run pytest e2e/ -v --tb=short --color=yes; then
    echo -e "${GREEN}✓ E2E tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ E2E tests failed${NC}"
    exit 1
fi
