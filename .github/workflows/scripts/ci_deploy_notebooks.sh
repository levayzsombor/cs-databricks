#!/usr/bin/env bash
set -euo pipefail

# Deploy Databricks notebooks for a target environment.
if [[ "$#" -lt 3 || "$#" -gt 5 ]]; then
  echo "Usage: $0 <environment> <branch> <databricks_host> [output_file] [append_output]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

environment="$1"
branch="$2"
databricks_host="$3"
output_file="${4:-deployment-result.json}"
append_output="${5:-false}"

python "$SCRIPT_DIR/deploy-notebooks.py" \
  --environment "$environment" \
  --branch "$branch" \
  --databricks-host "$databricks_host" \
  --output-file "$output_file"

if [[ "$append_output" == "true" ]]; then
  : "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set when append_output=true}"
  cat "$output_file" >>"$GITHUB_OUTPUT"
fi
