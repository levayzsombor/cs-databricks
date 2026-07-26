#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../../.." && pwd)"
PRE_COMMIT_BIN="${REPO_ROOT}/.venv/bin/pre-commit"

if [[ ! -x "${PRE_COMMIT_BIN}" ]]; then
    echo "pre-commit not found at '${PRE_COMMIT_BIN}'. Run local environment setup first."
    exit 1
fi

cd "${REPO_ROOT}"
export PATH="${REPO_ROOT}/.venv/bin:${PATH}"
"${PRE_COMMIT_BIN}" run --all-files
