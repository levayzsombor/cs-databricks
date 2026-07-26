#!/usr/bin/env bash
set -euo pipefail

# Run smoke tests against a target Databricks environment.
if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <environment> <databricks_host>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

environment="$1"
databricks_host="$2"

python "$SCRIPT_DIR/smoke-tests.py" \
  --environment "$environment" \
  --databricks-host "$databricks_host"
