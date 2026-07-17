#!/usr/bin/env bash
set -euo pipefail

git fetch origin staging prod
git checkout -B prod origin/prod
git merge --no-ff --no-edit origin/staging
git push origin prod
