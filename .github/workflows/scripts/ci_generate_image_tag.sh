#!/usr/bin/env bash
set -euo pipefail

# Generate a deterministic image tag for CI builds.
if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <ref_name> <commit_sha>" >&2
  exit 1
fi

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set}"

ref_name="$1"
commit_sha="$2"

short_sha="$(echo "$commit_sha" | cut -c1-7)"
tag="${ref_name}-$(date +%Y%m%d-%H%M%S)-${short_sha}"

echo "tag=$tag" >>"$GITHUB_OUTPUT"
echo "Image tag: $tag"
