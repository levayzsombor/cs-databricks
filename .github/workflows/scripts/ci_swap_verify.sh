#!/usr/bin/env bash
set -euo pipefail

# Verify standby endpoint becomes active after swap.
if [[ "$#" -lt 3 || "$#" -gt 4 ]]; then
  echo "Usage: $0 <traffic_manager_profile> <resource_group> <standby_env> [wait_seconds]" >&2
  exit 1
fi

traffic_manager_profile="$1"
resource_group="$2"
standby_env="$3"
wait_seconds="${4:-0}"

if [[ "$wait_seconds" != "0" ]]; then
  sleep "$wait_seconds"
fi

new_status="$(az network traffic-manager endpoint show \
  --name "${standby_env}-endpoint" \
  --profile-name "$traffic_manager_profile" \
  --resource-group "$resource_group" \
  --type "externalEndpoints" \
  --query "properties.endpointStatus" -o tsv)"

if [[ "$new_status" != "Enabled" ]]; then
  echo "Swap verification failed for ${standby_env} endpoint"
  exit 1
fi

echo "Swap verified successfully"
echo "Active environment: ${standby_env}"
