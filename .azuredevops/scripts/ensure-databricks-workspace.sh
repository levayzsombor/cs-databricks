#!/usr/bin/env bash
set -euo pipefail

workspace_name="${DATABRICKS_WORKSPACE_NAME}"
resource_group="${AZURE_RESOURCE_GROUP}"
location="${AZURE_LOCATION}"

if az databricks workspace show --name "$workspace_name" --resource-group "$resource_group" >/dev/null 2>&1; then
  echo "Databricks workspace exists: $workspace_name"
else
  echo "Creating Databricks workspace: $workspace_name"
  az databricks workspace create \
    --name "$workspace_name" \
    --resource-group "$resource_group" \
    --location "$location" \
    --sku standard
fi

workspace_url=$(az databricks workspace show --name "$workspace_name" --resource-group "$resource_group" --query workspaceUrl -o tsv)
workspace_resource_id=$(az databricks workspace show --name "$workspace_name" --resource-group "$resource_group" --query id -o tsv)

echo "##vso[task.setvariable variable=DATABRICKS_HOST]https://${workspace_url}"
echo "##vso[task.setvariable variable=DATABRICKS_AZURE_RESOURCE_ID]${workspace_resource_id}"
