#!/usr/bin/env bash
set -euo pipefail

missing=0
for var_name in AZURE_SERVICE_CONNECTION AZURE_RESOURCE_GROUP AZURE_LOCATION DATABRICKS_TOKEN; do
  var_value="${!var_name:-}"
  if [[ -z "$var_value" || "$var_value" =~ ^\$\(.+\)$ ]]; then
    echo "Missing required variable: ${var_name}"
    missing=1
  fi
done

if [[ "$missing" -ne 0 ]]; then
  echo "Please set missing variables in Azure DevOps variable group 'databricks-dev' and authorize it for this pipeline."
  exit 1
fi
