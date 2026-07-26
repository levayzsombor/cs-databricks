#!/bin/bash
# Script to run linting and format checks
# Usage: ./lint-and-format.sh

set -euo pipefail

echo "🔍 Running ruff linting..."
pip install ruff
ruff check src/ tests/ --select E,W,F,I --show-fixes

echo "🔍 Running ruff formatting check..."
ruff format src/ tests/ --check

echo "✅ Linting completed successfully"
