#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/cs-databricks

pre-commit run --all-files
