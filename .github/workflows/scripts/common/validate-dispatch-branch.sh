#!/usr/bin/env bash
set -euo pipefail

expected_branch="${1:?expected branch argument is required}"

if [ "${GITHUB_REF_NAME}" != "${expected_branch}" ]; then
  echo "This workflow must be run from the ${expected_branch} branch. Selected branch: ${GITHUB_REF_NAME}" >&2
  exit 1
fi
