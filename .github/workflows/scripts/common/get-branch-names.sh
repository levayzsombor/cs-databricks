#!/usr/bin/env bash
set -euo pipefail

echo "SOURCE_BRANCH_NAME=$(echo ${GITHUB_HEAD_REF} | sed 's|refs/heads/||')" >> $GITHUB_ENV
echo "TARGET_BRANCH_NAME=$(echo ${GITHUB_BASE_REF} | sed 's|refs/heads/||')" >> $GITHUB_ENV