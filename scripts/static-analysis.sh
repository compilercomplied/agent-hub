#!/bin/bash
set -e

# Static Analysis Script
# This script is used both locally via mise and during the Docker build 
# to ensure consistent linting and type checking across environments.

# Ensure uv is in PATH
if ! command -v uv &> /dev/null; then
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "--- Running Ruff (Linting) ---"
uv run ruff check .

echo ""
echo "--- Running Basedpyright (Type Checking) ---"
uv run basedpyright
