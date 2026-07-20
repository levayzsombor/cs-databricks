#!/usr/bin/env bash
set -euo pipefail

RESULTS_DIR="test_results"
STORAGE_ACCOUNT_NAME="lzsstorageaccount"
CONTAINER_NAME="github-artifacts"

if [[ ! -d "${RESULTS_DIR}" ]]; then
  echo "No '${RESULTS_DIR}' directory found. Nothing to upload."
  exit 1
fi

echo "Uploading '${RESULTS_DIR}' to storage account '${STORAGE_ACCOUNT_NAME}', container '${CONTAINER_NAME}'..."
az storage blob upload-batch \
  --account-name "${STORAGE_ACCOUNT_NAME}" \
  --destination "${CONTAINER_NAME}" \
  --source "${RESULTS_DIR}" \
  --auth-mode login \
  --overwrite true

echo "Upload complete."
