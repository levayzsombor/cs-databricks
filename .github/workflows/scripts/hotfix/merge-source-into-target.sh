#!/usr/bin/env bash
set -euo pipefail

git fetch origin "${SOURCE_BRANCH}" "${TARGET_BRANCH}"
git checkout -B "${TARGET_BRANCH}" "origin/${TARGET_BRANCH}"
git merge --no-ff --no-edit "origin/${SOURCE_BRANCH}"
git push origin "${TARGET_BRANCH}"
