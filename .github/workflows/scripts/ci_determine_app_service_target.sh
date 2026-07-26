#!/usr/bin/env bash
set -euo pipefail

# Map branch ref to App Service deployment target.
if [[ "$#" -ne 1 ]]; then
  echo "Usage: $0 <github_ref>" >&2
  exit 1
fi

: "${GITHUB_OUTPUT:?GITHUB_OUTPUT must be set}"

github_ref="$1"

if [[ "$github_ref" == "refs/heads/prod" ]]; then
  {
    echo "app-service-name=app-countrystats-prod"
    echo "slot=staging"
    echo "environment=prod"
  } >>"$GITHUB_OUTPUT"
elif [[ "$github_ref" == "refs/heads/staging" ]]; then
  {
    echo "app-service-name=app-countrystats-staging"
    echo "slot=production"
    echo "environment=staging"
  } >>"$GITHUB_OUTPUT"
else
  {
    echo "app-service-name=app-countrystats-dev"
    echo "slot=production"
    echo "environment=dev"
  } >>"$GITHUB_OUTPUT"
fi
