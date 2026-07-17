#!/usr/bin/env bash
set -euo pipefail

az devops configure --defaults organization="$AZDO_ORG_URL" project="$AZDO_PROJECT"
az pipelines run --id "$PIPELINE_ID" --branch main
