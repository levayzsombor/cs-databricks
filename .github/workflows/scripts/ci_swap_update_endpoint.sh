#!/usr/bin/env bash
set -euo pipefail

# Update Traffic Manager endpoint status for blue/green slot.
if [[ "$#" -ne 4 ]]; then
  echo "Usage: $0 <traffic_manager_profile> <resource_group> <env_name> <endpoint_status>" >&2
  exit 1
fi

traffic_manager_profile="$1"
resource_group="$2"
env_name="$3"
endpoint_status="$4"

az network traffic-manager endpoint update \
  --name "${env_name}-endpoint" \
  --profile-name "$traffic_manager_profile" \
  --resource-group "$resource_group" \
  --type "externalEndpoints" \
  --endpoint-status "$endpoint_status"

echo "Set ${env_name} endpoint to ${endpoint_status}"
