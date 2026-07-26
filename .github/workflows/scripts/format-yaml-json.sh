#!/bin/bash
# Script to format and validate YAML/JSON files with prettier
# Usage: ./format-yaml-json.sh

set -euo pipefail

echo "🎨 Installing prettier..."
npm install -g prettier

echo "🎨 Formatting YAML files..."
find .github/workflows -name "*.yml" -o -name "*.yaml" | xargs prettier --write

echo "🎨 Formatting JSON files..."
find . -name "*.json" -not -path "./node_modules/*" -not -path "./.git/*" | xargs prettier --write

echo "✅ YAML/JSON formatting completed"
