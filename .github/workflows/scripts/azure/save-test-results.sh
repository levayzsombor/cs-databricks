#!/usr/bin/env bash
set -euo pipefail

RESULTS_DIR="test_results"
STORAGE_ACCOUNT_NAME="${STORAGE_ACCOUNT_NAME:-lzsstorageaccount}"
CONTAINER_NAME="${CONTAINER_NAME:-github-artifacts}"

TEST_RUN_TYPE_VALUE="${TEST_RUN_TYPE:-TEST_RUN}"
TARGET_ENV_VALUE="${TARGET_ENV:-unknown-env}"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
DESTINATION_PATH="${TARGET_ENV_VALUE}/${TEST_RUN_TYPE_VALUE}/${TIMESTAMP}"

AZDO_ORG_URL_VALUE="${AZDO_ORG_URL:-}"
AZDO_PROJECT_VALUE="${AZDO_PROJECT:-}"
AZDO_GITHUB_SERVICE_CONNECTION_VALUE="${AZDO_GITHUB_SERVICE_CONNECTION:-}"

if [[ ! -d "${RESULTS_DIR}" ]]; then
    echo "No '${RESULTS_DIR}' directory found. Nothing to upload."
    exit 1
fi

echo "Uploading '${RESULTS_DIR}' to storage account '${STORAGE_ACCOUNT_NAME}', container '${CONTAINER_NAME}', path '${DESTINATION_PATH}'..."
if [[ -n "${AZDO_ORG_URL_VALUE}" || -n "${AZDO_PROJECT_VALUE}" || -n "${AZDO_GITHUB_SERVICE_CONNECTION_VALUE}" ]]; then
    echo "Azure DevOps context detected (org/project/service-connection env vars are set)."
fi

# Prefer Entra ID (login) auth, but fall back to account key auth when
# the service principal lacks Storage Blob Data* roles.
if az storage blob upload-batch \
    --account-name "${STORAGE_ACCOUNT_NAME}" \
    --destination "${CONTAINER_NAME}" \
    --destination-path "${DESTINATION_PATH}" \
    --source "${RESULTS_DIR}" \
    --auth-mode login \
    --overwrite true; then
    echo "Upload complete using login auth."
    exit 0
fi

echo "Login auth upload failed. Retrying with account key auth..."
az storage blob upload-batch \
    --account-name "${STORAGE_ACCOUNT_NAME}" \
    --destination "${CONTAINER_NAME}" \
    --destination-path "${DESTINATION_PATH}" \
    --source "${RESULTS_DIR}" \
    --auth-mode key \
    --overwrite true

echo "Upload complete using key auth."
