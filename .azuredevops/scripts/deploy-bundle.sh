#!/usr/bin/env bash
set -euo pipefail

target_name="${1:?target name is required}"
export PATH="$HOME/.databricks/bin:$PATH"
databricks bundle deploy -t "$target_name"
