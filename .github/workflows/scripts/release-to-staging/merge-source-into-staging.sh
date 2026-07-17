#!/usr/bin/env bash
set -euo pipefail

git fetch origin "${SOURCE_BRANCH}" staging
git checkout -B staging origin/staging
git merge --no-ff --no-edit "origin/${SOURCE_BRANCH}"
git push origin staging
