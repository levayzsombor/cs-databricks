#!/usr/bin/env python3
"""
Deploy Databricks notebooks to specified environment.
Handles multiple environments (dev, ua, staging, blue, green).
Uses Databricks REST API with PAT authentication.
"""

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.workspace import ImportFormat


def deploy_notebooks(environment, branch, databricks_host):
    """Deploy notebooks from src/notebooks to Databricks workspace."""

    # Initialize Databricks client
    pat_token = os.getenv("DATABRICKS_PAT")
    if not pat_token:
        raise ValueError("DATABRICKS_PAT environment variable not set")

    client = WorkspaceClient(host=databricks_host, token=pat_token)

    deployment_info = {
        "environment": environment,
        "branch": branch,
        "timestamp": datetime.now(UTC).isoformat(),
        "databricks_host": databricks_host,
        "notebooks_deployed": [],
        "failures": [],
    }

    notebooks_dir = Path("src/notebooks")

    if not notebooks_dir.exists():
        print(f"⚠️ No notebooks directory found at {notebooks_dir}")
        return deployment_info

    for notebook_file in notebooks_dir.glob("*.ipynb"):
        notebook_path = f"/Shared/ci-cd/{environment}/{notebook_file.stem}"

        try:
            # Read notebook content
            with open(notebook_file, "rb") as f:
                notebook_content = f.read()

            # Upload to Databricks
            client.workspace.upload(
                path=notebook_path,
                content=notebook_content,
                overwrite=True,
                format=ImportFormat.JUPYTER,
            )

            deployment_info["notebooks_deployed"].append({
                "name": notebook_file.name,
                "path": notebook_path,
                "status": "success",
                "size_bytes": len(notebook_content),
            })

            print(f"✅ Deployed {notebook_file.name} to {notebook_path}")

        except Exception as e:
            error_msg = str(e)
            deployment_info["failures"].append({
                "notebook": notebook_file.name,
                "path": notebook_path,
                "error": error_msg,
            })
            print(f"❌ Failed to deploy {notebook_file.name}: {error_msg}")

    return deployment_info


def main():
    parser = argparse.ArgumentParser(description="Deploy Databricks notebooks")
    parser.add_argument("--environment", required=True, choices=["dev", "ua", "staging", "blue", "green"])
    parser.add_argument("--branch", required=True)
    parser.add_argument("--databricks-host", required=True)
    parser.add_argument("--output-file", default="deployment-result.json")

    args = parser.parse_args()

    try:
        result = deploy_notebooks(args.environment, args.branch, args.databricks_host)

        # Write result to file for subsequent steps
        with open(args.output_file, "w") as f:
            json.dump(result, f, indent=2)

        # Print result to stdout for debugging
        print("\n" + "=" * 80)
        print(json.dumps(result, indent=2))
        print("=" * 80 + "\n")

        # Exit with error if there were failures
        if result["failures"]:
            print(f"❌ Deployment completed with {len(result['failures'])} failure(s)")
            sys.exit(1)
        else:
            print(f"✅ All {len(result['notebooks_deployed'])} notebooks deployed successfully")
            sys.exit(0)

    except Exception as e:
        print(f"❌ Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
