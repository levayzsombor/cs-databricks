#!/bin/bash
# Script to check Python code style and format with ruff
# Usage: ./format-python.sh

set -euo pipefail

echo "🎨 Formatting Python code with ruff..."
pip install ruff
ruff format src/ tests/

echo "✅ Formatting completed"
