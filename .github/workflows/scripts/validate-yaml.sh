#!/bin/bash
# Script to validate YAML files for syntax errors
# Usage: ./validate-yaml.sh

set -euo pipefail

echo "✔️ Validating YAML files..."
pip install yamllint

find .github/workflows \( -name "*.yml" -o -name "*.yaml" \) | while read -r file; do
    echo "  Checking: $file"
    yamllint "$file"
done

echo "✅ YAML validation completed"
