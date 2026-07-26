#!/usr/bin/env bash
set -euo pipefail

# Send deployment metadata to Azure Log Analytics.
if [[ "$#" -lt 4 || "$#" -gt 5 ]]; then
  echo "Usage: $0 <workspace_id> <workspace_key> <environment> <status> [deployment_result_file]" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly SCRIPT_DIR

workspace_id="$1"
workspace_key="$2"
environment="$3"
status="$4"
deployment_result_file="${5:-deployment-result.json}"

python "$SCRIPT_DIR/send-logs-to-analytics.py" \
  --workspace-id "$workspace_id" \
  --workspace-key "$workspace_key" \
  --environment "$environment" \
  --status "$status" \
  --deployment-result "$deployment_result_file"
