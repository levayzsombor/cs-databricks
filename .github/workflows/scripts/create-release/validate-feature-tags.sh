#!/usr/bin/env bash
set -euo pipefail

git fetch origin --tags main ua staging prod

if [ -z "${FEATURE_TAGS:-}" ]; then
  echo "feature_tags input is required." >&2
  exit 1
fi

declare -A seen
valid_tags=()

IFS=',' read -r -a raw_tags <<<"${FEATURE_TAGS}"
for raw_tag in "${raw_tags[@]}"; do
  tag="$(printf '%s' "${raw_tag}" | xargs)"
  if [ -z "${tag}" ]; then
    continue
  fi

  if [[ ! "${tag}" =~ ^feature- ]]; then
    echo "Tag '${tag}' must start with 'feature-'." >&2
    exit 1
  fi

  if ! git rev-parse -q --verify "refs/tags/${tag}" >/dev/null; then
    echo "Tag '${tag}' does not exist." >&2
    exit 1
  fi

  if [ -n "${seen[${tag}]:-}" ]; then
    continue
  fi
  seen["${tag}"]=1
  valid_tags+=("${tag}")
done

if [ "${#valid_tags[@]}" -eq 0 ]; then
  echo "No valid tags were provided." >&2
  exit 1
fi

for tag in "${valid_tags[@]}"; do
  tag_commit="$(git rev-list -n 1 "refs/tags/${tag}")"
  for protected in main ua staging prod; do
    if git merge-base --is-ancestor "${tag_commit}" "origin/${protected}"; then
      echo "Tag '${tag}' is already on protected branch '${protected}'." >&2
      exit 1
    fi
  done
done

tags_csv="$(
  IFS=,
  echo "${valid_tags[*]}"
)"
echo "tags_csv=${tags_csv}" >>"${GITHUB_OUTPUT}"
