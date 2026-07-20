#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/../common/branch-utils.sh"

git fetch --tags --force

latest_version_tag="$(branch_utils_latest_tag 'version-*')"
if [[ -z "$latest_version_tag" ]]; then
    echo "No version tag found. Create a version tag before opening a version update branch."
    exit 1
fi

version="$(branch_utils_parse_version "$latest_version_tag")"
branch_name="dev-version-${version}_update"

git switch -c "$branch_name" "$latest_version_tag"
git push -u origin "$branch_name"

gh pr create \
    --base main \
    --head "$branch_name" \
    --title "Create version update branch from ${latest_version_tag}" \
    --body "Creates the dev-version update branch from ${latest_version_tag}." \
    --label "MINOR"
