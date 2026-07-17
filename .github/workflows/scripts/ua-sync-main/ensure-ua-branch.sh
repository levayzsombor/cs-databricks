#!/usr/bin/env bash
set -euo pipefail

git fetch origin main

if git ls-remote --exit-code --heads origin ua >/dev/null; then
  echo "ua branch already exists"
else
  git checkout -B ua origin/main
  git push origin ua
fi
