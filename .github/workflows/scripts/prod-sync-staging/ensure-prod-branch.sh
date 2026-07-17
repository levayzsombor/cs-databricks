#!/usr/bin/env bash
set -euo pipefail

git fetch origin staging

if git ls-remote --exit-code --heads origin prod >/dev/null; then
  echo "prod branch already exists"
else
  git checkout -B prod origin/staging
  git push origin prod
fi
