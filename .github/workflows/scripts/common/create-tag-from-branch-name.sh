#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/branch-utils.sh"

branch_utils_create_and_push_tag "${TARGET_BRANCH:-$(branch_utils_target_branch)}"
