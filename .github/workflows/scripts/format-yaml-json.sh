#!/bin/bash
# Script to format and validate YAML/JSON files with prettier
# Usage: ./format-yaml-json.sh

set -euo pipefail

echo "🎨 Installing prettier..."
npm install -g prettier

echo "🎨 Formatting YAML files..."
find .github/workflows \( -name "*.yml" -o -name "*.yaml" \) -print0 | xargs -0 prettier --write

echo "🎨 Formatting JSON files..."
find . -name "*.json" -not -path "./node_modules/*" -not -path "./.git/*" -print0 | xargs -0 prettier --write

echo "✅ YAML/JSON formatting completed"
