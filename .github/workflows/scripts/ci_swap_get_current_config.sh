#!/usr/bin/env bash
set -euo pipefail

# Read current blue/green active endpoint from Traffic Manager.
if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <traffic_manager_profile> <resource_group>" >&2
  exit 1
fi

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set}"

traffic_manager_profile="$1"
resource_group="$2"

active_status="$(az network traffic-manager endpoint show \
  --name "blue-endpoint" \
  --profile-name "$traffic_manager_profile" \
  --resource-group "$resource_group" \
  --type "externalEndpoints" \
  --query "properties.endpointStatus" -o tsv)"

if [[ "$active_status" == "Enabled" ]]; then
  echo "active-env=blue" >>"$GITHUB_OUTPUT"
  echo "standby-env=green" >>"$GITHUB_OUTPUT"
else
  echo "active-env=green" >>"$GITHUB_OUTPUT"
  echo "standby-env=blue" >>"$GITHUB_OUTPUT"
fi
