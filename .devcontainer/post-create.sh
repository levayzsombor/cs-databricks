#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/cs-databricks

python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip install pre-commit pytest pytest-mock ruff ty
npm i

# Install uv when feature is unavailable or not yet present on PATH
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Install Databricks CLI
if ! command -v databricks >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sudo sh
fi
