#!/usr/bin/env sh
set -eu

case "$(uname -s)" in
  MINGW* | MSYS* | CYGWIN*)
    echo "Skipping POSIX Docker wait on Windows host shell."
    exit 0
    ;;
esac

if [ -n "${WSL_DISTRO_NAME:-}" ] || grep -qi microsoft /proc/version 2>/dev/null; then
  echo "Skipping POSIX Docker wait inside WSL-hosted Bash on Windows."
  exit 0
fi

timeout_seconds=90
start_time=$(date +%s)

echo "Waiting for Docker engine to become ready..."

while true; do
  if ready=$(docker version --format '{{if .Server}}ready{{else}}not-ready{{end}}' 2>/dev/null); then
    if [ "$ready" = "ready" ]; then
      echo "Docker engine is ready."
      exit 0
    fi
  fi

  now=$(date +%s)
  elapsed=$((now - start_time))
  if [ "$elapsed" -ge "$timeout_seconds" ]; then
    echo "Docker did not become ready within ${timeout_seconds} seconds." >&2
    exit 1
  fi

  sleep 1
done
