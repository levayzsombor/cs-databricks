#!/usr/bin/env bash
set -euo pipefail

TEST_STEP_OUTCOME="${TEST_STEP_OUTCOME:-unknown}"

if [[ "${TEST_STEP_OUTCOME}" != "success" ]]; then
    echo "Test step failed earlier. Marking job as failed at the end."
    exit 1
fi

echo "Test step outcome is success."
