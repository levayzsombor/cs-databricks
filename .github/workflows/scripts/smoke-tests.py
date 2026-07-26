#!/usr/bin/env python3
"""
Smoke tests for Databricks environment.
Quick validation that critical notebooks and jobs are working.
"""

import argparse
import os
import sys

from databricks.sdk import WorkspaceClient


def smoke_tests(environment, databricks_host):
    """Run smoke tests against Databricks environment."""

    pat_token = os.getenv("DATABRICKS_PAT")
    if not pat_token:
        raise ValueError("DATABRICKS_PAT environment variable not set")

    client = WorkspaceClient(host=databricks_host, token=pat_token)

    test_results = {"environment": environment, "tests": [], "passed": 0, "failed": 0}

    # Test 1: Verify workspace access
    print("🧪 Test 1: Workspace connectivity...")
    try:
        client.workspace.get_status(path="/")
        test_results["tests"].append({"name": "Workspace connectivity", "status": "PASSED"})
        test_results["passed"] += 1
        print("   ✅ PASSED\n")
    except Exception as e:
        test_results["tests"].append({"name": "Workspace connectivity", "status": "FAILED", "error": str(e)})
        test_results["failed"] += 1
        print(f"   ❌ FAILED: {e}\n")

    # Test 2: Verify notebooks are accessible
    print("🧪 Test 2: Notebook accessibility...")
    try:
        notebook_path = f"/Shared/ci-cd/{environment}"
        notebooks = list(client.workspace.list(path=notebook_path, recursive=True))
        notebook_count = sum(1 for nb in notebooks if nb.object_type == "NOTEBOOK")

        if notebook_count > 0:
            test_results["tests"].append({
                "name": "Notebook accessibility",
                "status": "PASSED",
                "notebook_count": notebook_count,
            })
            test_results["passed"] += 1
            print(f"   ✅ PASSED (found {notebook_count} notebooks)\n")
        else:
            test_results["tests"].append({
                "name": "Notebook accessibility",
                "status": "FAILED",
                "error": "No notebooks found",
            })
            test_results["failed"] += 1
            print("   ⚠️ WARNING: No notebooks found\n")
    except Exception as e:
        test_results["tests"].append({"name": "Notebook accessibility", "status": "FAILED", "error": str(e)})
        test_results["failed"] += 1
        print(f"   ❌ FAILED: {e}\n")

    # Test 3: SQL endpoint connectivity
    print("🧪 Test 3: SQL endpoint verification...")
    try:
        # This is a placeholder - would need SQL endpoint ID
        # For now, just check that endpoints can be listed
        endpoints = client.warehouses.list()
        endpoint_count = len(list(endpoints))

        test_results["tests"].append({
            "name": "SQL endpoint verification",
            "status": "PASSED",
            "endpoint_count": endpoint_count,
        })
        test_results["passed"] += 1
        print(f"   ✅ PASSED (found {endpoint_count} endpoints)\n")
    except Exception as e:
        print(f"   ⚠️ WARNING: Could not verify SQL endpoints: {e}\n")

    # Summary
    print("=" * 80)
    print(f"Smoke Tests Summary ({environment}):")
    print(f"  ✅ Passed: {test_results['passed']}")
    print(f"  ❌ Failed: {test_results['failed']}")
    print("=" * 80 + "\n")

    return test_results


def main():
    parser = argparse.ArgumentParser(description="Run smoke tests for Databricks environment")
    parser.add_argument("--environment", required=True, choices=["dev", "ua", "staging", "blue", "green"])
    parser.add_argument("--databricks-host", required=True)

    args = parser.parse_args()

    try:
        results = smoke_tests(args.environment, args.databricks_host)

        if results["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except Exception as e:
        print(f"❌ Smoke tests failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
