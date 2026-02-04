#!/usr/bin/env bash

# run-e2e.sh - Script to run end-to-end tests using Docker Compose
#
# This script simplifies the execution of e2e tests by:
# 1. Building the Docker images
# 2. Starting the API service
# 3. Running the tests
# 4. Cleaning up resources
#
# Usage: ./scripts/run-e2e.sh

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

echo -e "${YELLOW}Starting e2e test run...${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker compose -f docker-compose.e2e.yaml down -v --remove-orphans 2>/dev/null || true
}

# Set trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Build and run tests
echo -e "${YELLOW}Building Docker images...${NC}"
if ! docker compose -f docker-compose.e2e.yaml build; then
    echo -e "${RED}Failed to build Docker images${NC}"
    exit 1
fi

echo -e "${YELLOW}Starting services and running tests...${NC}"
if docker compose -f docker-compose.e2e.yaml up --abort-on-container-exit --exit-code-from e2e-tests; then
    echo -e "${GREEN}✓ E2E tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ E2E tests failed${NC}"
    exit 1
fi
