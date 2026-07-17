#!/usr/bin/env bash
set -euo pipefail

git fetch origin main ua
git checkout -B ua origin/ua
git merge --no-ff --no-edit origin/main
git push origin ua
