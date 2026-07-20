#!/usr/bin/env bash
set -euo pipefail

source_branch_name="${GITHUB_HEAD_REF#refs/heads/}"
target_branch_name="${GITHUB_BASE_REF#refs/heads/}"

echo "SOURCE_BRANCH_NAME=${source_branch_name}" >>"${GITHUB_ENV}"
echo "TARGET_BRANCH_NAME=${target_branch_name}" >>"${GITHUB_ENV}"
