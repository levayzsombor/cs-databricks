#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/../common/branch-utils.sh"

feature_tags_csv="${FEATURE_TAGS:-}"
if [[ -z "$feature_tags_csv" ]]; then
    echo "FEATURE_TAGS input is required."
    exit 1
fi

git fetch --tags --force

selected_tags=()
IFS=',' read -r -a raw_selected <<<"$feature_tags_csv"
for tag in "${raw_selected[@]}"; do
    trimmed="${tag//[[:space:]]/}"
    [[ -n "$trimmed" ]] && selected_tags+=("$trimmed")
done

if [[ "${#selected_tags[@]}" -eq 0 ]]; then
    echo "No feature tags were provided."
    exit 1
fi

base_ref="$(branch_utils_latest_tag 'version-*')"
if [[ -z "$base_ref" ]]; then
    base_ref="main"
fi

branch_name="pre-release-$(date +%Y%m%d%H%M%S)"
git switch -c "$branch_name" "$base_ref"

declare -A seen_tags=()
tags_to_pick=()

for tag in "${selected_tags[@]}"; do
    if git rev-parse --verify "refs/tags/${tag}" >/dev/null 2>&1 && [[ -z "${seen_tags[$tag]:-}" ]]; then
        tags_to_pick+=("$tag")
        seen_tags["$tag"]=1
    fi
done

while IFS= read -r tag; do
    [[ -z "$tag" ]] && continue
    if [[ -z "${seen_tags[$tag]:-}" ]]; then
        tags_to_pick+=("$tag")
        seen_tags["$tag"]=1
    fi
done < <(git for-each-ref --sort=creatordate --format='%(refname:strip=2)' 'refs/tags/hotfix-*' 'refs/tags/version-*')

for tag in "${tags_to_pick[@]}"; do
    commit_sha="$(git rev-list -n 1 "$tag")"
    git cherry-pick "$commit_sha"
done

git push -u origin "$branch_name"

pr_label="PATCH"
for tag in "${selected_tags[@]}"; do
    case "$tag" in
    version-*)
        pr_label="MAJOR"
        break
        ;;
    feature-*)
        pr_label="MINOR"
        ;;
    esac
done

gh pr create \
    --base staging \
    --head "$branch_name" \
    --title "Create prerelease branch from feature tags" \
    --body "Creates the prerelease branch from selected feature tags: ${selected_tags[*]}." \
    --label "$pr_label"
