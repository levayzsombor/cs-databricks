#!/bin/bash
# Script to run tests on the Python project
# Usage: ./run-tests.sh

set -euo pipefail

echo "🧪 Installing test dependencies..."
pip install -r requirements-dev.txt

echo "🧪 Running pytest..."
pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

echo "✅ Tests completed"
