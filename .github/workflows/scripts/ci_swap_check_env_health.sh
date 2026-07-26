#!/usr/bin/env bash
set -euo pipefail

# Check health for a blue/green Databricks environment and emit a boolean output.
if [[ "$#" -lt 2 || "$#" -gt 3 ]]; then
  echo "Usage: $0 <environment> <databricks_host> [timeout_seconds]" >&2
  exit 1
fi

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

environment="$1"
databricks_host="$2"
timeout_seconds="${3:-60}"

if python "$SCRIPT_DIR/health-check.py" \
  --environment "$environment" \
  --databricks-host "$databricks_host" \
  --timeout "$timeout_seconds"; then
  echo "healthy=true" >>"$GITHUB_OUTPUT"
else
  echo "healthy=false" >>"$GITHUB_OUTPUT"
fi
