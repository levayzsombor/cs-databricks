#!/usr/bin/env bash
set -euo pipefail

check_command() {
  local cmd="$1"
  command -v "$cmd" >/dev/null 2>&1
}

echo "[auth-check] Verifying CLI auth state"

if check_command gh; then
  echo "[auth-check] gh"
  gh auth status >/dev/null 2>&1 && echo "  GitHub CLI: logged in" || echo "  GitHub CLI: not logged in"
fi

if check_command az; then
  echo "[auth-check] az"
  az account show >/dev/null 2>&1 && echo "  Azure CLI: logged in" || echo "  Azure CLI: not logged in"
fi

if check_command databricks; then
  echo "[auth-check] databricks"
  databricks auth profiles >/dev/null 2>&1 && echo "  Databricks CLI: profile available" || echo "  Databricks CLI: profile missing"
fi

if check_command git; then
  echo "[auth-check] git"
  if git config --global --get user.name >/dev/null 2>&1; then
    echo "  Git: user configured"
  else
    echo "  Git: user not configured"
  fi
fi
