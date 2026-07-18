#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/cs-databricks

python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
npm i

