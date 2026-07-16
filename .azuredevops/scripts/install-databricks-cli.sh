#!/usr/bin/env bash
set -euo pipefail

curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh
echo "##vso[task.prependpath]$HOME/.databricks/bin"
