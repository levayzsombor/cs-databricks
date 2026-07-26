#!/usr/bin/env bash
set -euo pipefail

# Resolve production deployment target metadata.
if [[ "$#" -ne 0 ]]; then
  echo "Usage: $0" >&2
  exit 1
fi

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set}"

# Default production target. Can be extended to query active color dynamically.
{
  echo "target-env=blue"
  echo "databricks-host=https://adb-7405606075384170.10.azuredatabricks.net"
  echo "databricks-pat-secret=DATABRICKS_BLUE_PAT"
} >>"$GITHUB_OUTPUT"
