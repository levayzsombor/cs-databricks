#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/cs-databricks

python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
uv self update
uv pip install -r requirements-dev.txt
npm i

