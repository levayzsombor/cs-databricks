#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/branch-utils.sh"

branch_utils_validate_source_branch "${TARGET_BRANCH:-$(branch_utils_target_branch)}"
