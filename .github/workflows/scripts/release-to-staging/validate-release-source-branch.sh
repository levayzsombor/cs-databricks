#!/usr/bin/env bash
set -euo pipefail

target_branch="staging"

if [ -z "${SOURCE_BRANCH:-}" ]; then
  echo "source_branch is required." >&2
  exit 1
fi

if [ "${SOURCE_BRANCH}" = "${target_branch}" ]; then
  echo "source_branch must be different from staging." >&2
  exit 1
fi

git fetch origin "${SOURCE_BRANCH}" "${target_branch}" --tags

if ! git rev-parse --verify "origin/${SOURCE_BRANCH}" >/dev/null 2>&1; then
  echo "Source branch '${SOURCE_BRANCH}' does not exist." >&2
  exit 1
fi

if ! git rev-parse --verify "origin/${target_branch}" >/dev/null 2>&1; then
  echo "Target branch '${target_branch}' does not exist." >&2
  exit 1
fi

release_tags="$(git tag --points-at "origin/${SOURCE_BRANCH}" | grep 'release' || true)"
if [ -z "${release_tags}" ]; then
  echo "Source branch '${SOURCE_BRANCH}' does not point at a Git tag containing 'release'." >&2
  exit 1
fi

echo "Validated release tag(s) on ${SOURCE_BRANCH}:"
printf '%s\n' "${release_tags}"
