#!/usr/bin/env python3
"""Validate source branch naming rules based on target branch."""

import os
import sys

DEV_ALLOWED = ["feature-", "hotfix-", "dev-version"]
STAGING_ALLOWED = ["prerelease-", "hotfix"]
PROD_ALLOWED = ["staging"]

BRANCH_RULES = {
    "dev": {"match": "prefix", "allowed": DEV_ALLOWED},
    "staging": {"match": "prefix", "allowed": STAGING_ALLOWED},
    "prod": {"match": "exact", "allowed": PROD_ALLOWED},
}


def read_branch_env(var_name: str) -> str:
    return os.getenv(var_name, "").strip()


def main() -> int:
    source_branch_name = read_branch_env("SOURCE_BRANCH_NAME")
    target_branch_name = read_branch_env("TARGET_BRANCH_NAME")

    rule = BRANCH_RULES.get(target_branch_name)
    if rule is None:
        print(
            f"Branch name check skipped: TARGET_BRANCH_NAME='{target_branch_name or 'N/A'}' has no branch naming rule."
        )
        return 0

    if not source_branch_name:
        print(
            "Branch name check failed: "
            f"SOURCE_BRANCH_NAME is empty while TARGET_BRANCH_NAME is '{target_branch_name}'.",
            file=sys.stderr,
        )
        return 1

    allowed = rule["allowed"]
    matches = (
        source_branch_name.startswith(tuple(allowed)) if rule["match"] == "prefix" else source_branch_name in allowed
    )
    if not matches:
        allowed_label = "Allowed prefixes" if rule["match"] == "prefix" else "Allowed source branches"
        print(
            "Branch name check failed: "
            f"SOURCE_BRANCH_NAME='{source_branch_name}' is invalid for TARGET_BRANCH_NAME='{target_branch_name}'. "
            f"{allowed_label}: {' | '.join(allowed)}.",
            file=sys.stderr,
        )
        return 1

    print(
        "Branch name check passed: "
        f"SOURCE_BRANCH_NAME='{source_branch_name}' is valid for TARGET_BRANCH_NAME='{target_branch_name}'."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
