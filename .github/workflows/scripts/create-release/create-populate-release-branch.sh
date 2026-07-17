#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PR_BRANCHES:-}" ]; then
  echo "No PR branches were resolved." >&2
  exit 1
fi

release_branch="release-$(date -u +%Y%m%d-%H%M%S)"

git fetch origin main
git checkout -B "${release_branch}" origin/main

IFS=',' read -r -a branches <<<"${PR_BRANCHES}"
for branch in "${branches[@]}"; do
  git fetch --no-tags origin "${branch}"
  git merge --no-ff --no-edit "origin/${branch}"
done

git push origin "${release_branch}"

echo "release_branch=${release_branch}" >>"${GITHUB_OUTPUT}"
echo "Created release branch '${release_branch}' from branches: ${PR_BRANCHES}"
