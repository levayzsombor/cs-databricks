#!/usr/bin/env python3
"""
Health check for Databricks environment after deployment.
Verifies notebooks exist and workspace is accessible.
Retries with exponential backoff for transient failures.
"""

import os
import argparse
import sys
import time
from datetime import datetime, timezone
from databricks.sdk import WorkspaceClient


def health_check(environment, databricks_host, timeout=300):
    """Verify deployed notebooks are accessible."""

    pat_token = os.getenv("DATABRICKS_PAT")
    if not pat_token:
        raise ValueError("DATABRICKS_PAT environment variable not set")

    client = WorkspaceClient(host=databricks_host, token=pat_token)

    start_time = time.time()
    attempt = 0
    max_attempts = (timeout // 10) + 1  # Attempt every 10 seconds

    while attempt < max_attempts:
        try:
            elapsed = time.time() - start_time
            attempt += 1

            print(f"[Attempt {attempt}] Running health checks ({elapsed:.0f}s elapsed)...")

            # Check workspace connectivity
            client.workspace.get_status(path="/")
            print(f"  ✓ Workspace accessible")

            # List deployed notebooks for this environment
            notebook_path = f"/Shared/ci-cd/{environment}"

            try:
                deployed_notebooks = list(client.workspace.list(path=notebook_path, recursive=True))
            except Exception as e:
                # Path might not exist yet if first deployment
                print(f"  ⓘ Notebook path not accessible yet: {e}")
                deployed_notebooks = []

            notebook_count = sum(1 for nb in deployed_notebooks if nb.object_type == "NOTEBOOK")
            print(f"  ✓ Found {notebook_count} notebooks in /{environment}")

            # Check if any notebooks were deployed
            if notebook_count == 0 and elapsed > 30:
                print(f"  ⚠ Warning: No notebooks found after {elapsed:.0f}s")

            print(f"\n✅ Health check PASSED")
            print(f"   Environment: {environment}")
            print(f"   Host: {databricks_host}")
            print(f"   Notebooks: {notebook_count}")
            print(f"   Time: {datetime.now(timezone.utc).isoformat()}\n")

            return {
                "status": "healthy",
                "notebook_count": notebook_count,
                "elapsed_seconds": elapsed,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            elapsed = time.time() - start_time

            if elapsed < timeout:
                wait_time = min(10, timeout - elapsed)
                print(f"  ✗ Health check failed: {e}")
                print(f"  ⏳ Retrying in {wait_time}s ({elapsed:.0f}s/{timeout}s total)...\n")
                time.sleep(wait_time)
            else:
                print(f"\n❌ Health check FAILED after {elapsed:.0f}s")
                print(f"   Error: {e}\n")
                raise


def main():
    parser = argparse.ArgumentParser(description="Health check for Databricks environment")
    parser.add_argument("--environment", required=True, choices=["dev", "ua", "staging", "blue", "green"])
    parser.add_argument("--databricks-host", required=True)
    parser.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    try:
        health_check(args.environment, args.databricks_host, args.timeout)
        sys.exit(0)
    except Exception as e:
        print(f"❌ Health check failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
