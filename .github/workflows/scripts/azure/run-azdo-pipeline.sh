#!/usr/bin/env bash
set -euo pipefail

pipeline_name="${PIPELINE_NAME:-}"
pipeline_id="${PIPELINE_ID:-}"
pipeline_branch="${PIPELINE_BRANCH:-${GITHUB_REF_NAME:-main}}"

az devops configure --defaults organization="$AZDO_ORG_URL" project="$AZDO_PROJECT"

if [[ -z "$pipeline_id" ]]; then
    if [[ -z "$pipeline_name" ]]; then
        echo "PIPELINE_NAME or PIPELINE_ID is required."
        exit 1
    fi

    pipeline_id="$(az pipelines show --name "$pipeline_name" --query id -o tsv)"
fi

az pipelines run --id "$pipeline_id" --branch "$pipeline_branch"
