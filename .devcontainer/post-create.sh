#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/cs-databricks

if ! command -v shellcheck >/dev/null 2>&1 || ! command -v shfmt >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y shellcheck shfmt
fi

mkdir -p /home/vscode/.local/bin

arch=$(uname -m)
case "$arch" in
  x86_64) actionlint_arch=amd64 ;;
  aarch64 | arm64) actionlint_arch=arm64 ;;
  *)
    echo "Unsupported architecture for actionlint: $arch" >&2
    exit 1
    ;;
esac

actionlint_version=v1.7.8
actionlint_url="https://github.com/rhysd/actionlint/releases/download/${actionlint_version}/actionlint_${actionlint_version#v}_linux_${actionlint_arch}.tar.gz"
actionlint_tmpdir=$(mktemp -d)
trap 'rm -rf "$actionlint_tmpdir"' EXIT
curl -fsSL "$actionlint_url" -o "$actionlint_tmpdir/actionlint.tar.gz"
tar -xzf "$actionlint_tmpdir/actionlint.tar.gz" -C "$actionlint_tmpdir"
install -m 0755 "$actionlint_tmpdir/actionlint" /home/vscode/.local/bin/actionlint

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
