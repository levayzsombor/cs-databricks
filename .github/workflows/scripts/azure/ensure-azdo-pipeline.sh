#!/usr/bin/env bash
set -euo pipefail

az devops configure --defaults organization="$AZDO_ORG_URL" project="$AZDO_PROJECT"

pipeline_id=$(az pipelines list --query "[?name=='${PIPELINE_NAME}'].id | [0]" -o tsv)

if [ -z "${pipeline_id}" ]; then
  echo "Creating Azure DevOps pipeline: ${PIPELINE_NAME}"
  pipeline_id=$(az pipelines create \
    --name "${PIPELINE_NAME}" \
    --repository "${GITHUB_REPOSITORY}" \
    --repository-type github \
    --branch main \
    --yml-path "${PIPELINE_YAML_PATH}" \
    --service-connection "${AZDO_GITHUB_SERVICE_CONNECTION}" \
    --skip-first-run true \
    --query id \
    -o tsv)
fi

echo "PIPELINE_ID=${pipeline_id}" >>"$GITHUB_ENV"
