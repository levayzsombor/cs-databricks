#!/usr/bin/env bash
set -euo pipefail

TEST_RUN_TYPE_VALUE="${TEST_RUN_TYPE:-TEST_RUN}"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"
RESULTS_DIR="test_results"
RESULTS_FILE="${RESULTS_DIR}/${TEST_RUN_TYPE_VALUE}_${TIMESTAMP}.txt"

mkdir -p "${RESULTS_DIR}"

./.venv/bin/python -m pytest 2>&1 | tee "${RESULTS_FILE}"
