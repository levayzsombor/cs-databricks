#!/usr/bin/env bash
set -euo pipefail

# Fail swap when either health check indicates unhealthy status.
if [[ "$#" -ne 2 ]]; then
  echo "Usage: $0 <blue_health> <green_health>" >&2
  exit 1
fi

blue_health="$1"
green_health="$2"

echo "Health checks failed!"
echo "BLUE: ${blue_health}"
echo "GREEN: ${green_health}"
exit 1
