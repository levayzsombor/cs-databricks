#!/usr/bin/env bash
set -euo pipefail

# Run Databricks health checks for a target environment.
if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  echo "Usage: $0 <environment> <databricks_host> [timeout_seconds]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

environment="$1"
databricks_host="$2"
timeout_seconds="${3:-300}"

python "$SCRIPT_DIR/health-check.py" \
  --environment "$environment" \
  --databricks-host "$databricks_host" \
  --timeout "$timeout_seconds"
