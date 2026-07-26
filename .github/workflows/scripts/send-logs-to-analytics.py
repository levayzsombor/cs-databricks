#!/usr/bin/env python3
"""
Send deployment logs to Azure Log Analytics.
Structured logging for monitoring, troubleshooting, and audit trails.
"""

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
from datetime import datetime, timezone

import requests


def send_to_log_analytics(workspace_id, workspace_key, environment, status, deployment_result_file):
    """Send structured logs to Log Analytics."""

    # Read deployment result if it exists
    deployment_data = {}
    if os.path.exists(deployment_result_file):
        try:
            with open(deployment_result_file, "r") as f:
                deployment_data = json.load(f)
        except Exception as e:
            print(f"⚠️ Could not read deployment result: {e}")

    # Prepare log entry
    log_entry = {
        "environment": environment,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "deployment": deployment_data,
        "workflow_run_id": os.getenv("GITHUB_RUN_ID"),
        "workflow_run_number": os.getenv("GITHUB_RUN_NUMBER"),
        "repository": os.getenv("GITHUB_REPOSITORY"),
        "branch": os.getenv("GITHUB_REF_NAME"),
        "actor": os.getenv("GITHUB_ACTOR"),
        "commit_sha": (os.getenv("GITHUB_SHA") or "")[:7],  # Short commit hash
    }

    # Build Log Analytics request
    log_type = "DatabricksDeployment"
    json_data = json.dumps(log_entry)
    body = json_data.encode("utf-8")

    # Create authorization signature
    rfc1123date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    content_length = len(body)

    try:
        signature = _build_signature(workspace_id, workspace_key, content_length, rfc1123date)
    except Exception as e:
        print(f"❌ Failed to build signature: {e}", file=sys.stderr)
        return False

    headers = {
        "Content-Type": "application/json",
        "Log-Type": log_type,
        "x-ms-date": rfc1123date,
        "Authorization": signature,
        "time-generated-field": "timestamp",
    }

    # Send to Log Analytics
    uri = f"https://{workspace_id}.ods.opinsights.azure.com/api/logs?api-version=2016-04-01"

    try:
        response = requests.post(uri, data=body, headers=headers, timeout=30)

        if response.status_code == 200:
            print("✅ Deployment log sent to Log Analytics")
            print(f"   Environment: {environment}")
            print(f"   Status: {status}")
            print(f"   Workspace ID: {workspace_id}")
            return True
        elif response.status_code == 201:
            print("✅ Deployment log ingested (accepted)")
            return True
        else:
            print(f"⚠️ Log Analytics response: {response.status_code}")
            print(f"   Body: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print("⚠️ Timeout sending logs to Log Analytics (continuing anyway)")
        return True  # Don't fail the job if Log Analytics is slow
    except Exception as e:
        print(f"⚠️ Failed to send logs to Log Analytics: {e}")
        return True  # Don't fail the job if logging fails


def _build_signature(workspace_id, workspace_key, content_length, rfc1123date):
    """Build authorization signature for Log Analytics."""

    # Create the authorization header
    string_to_hash = f"POST\n{content_length}\napplication/json\nx-ms-date:{rfc1123date}\n/api/logs"

    try:
        decoded_key = base64.b64decode(workspace_key)
    except Exception as e:
        raise ValueError(f"Invalid workspace key (must be base64): {e}")

    encoded_hash = base64.b64encode(
        hmac.new(decoded_key, string_to_hash.encode("utf-8"), hashlib.sha256).digest()
    ).decode("utf-8")

    authorization = f"SharedKey {workspace_id}:{encoded_hash}"
    return authorization


def main():
    parser = argparse.ArgumentParser(description="Send logs to Azure Log Analytics")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--workspace-key", required=True)
    parser.add_argument("--environment", required=True, choices=["dev", "ua", "staging", "blue", "green", "prod"])
    parser.add_argument("--status", required=True)
    parser.add_argument("--deployment-result", required=True)

    args = parser.parse_args()

    success = send_to_log_analytics(
        args.workspace_id, args.workspace_key, args.environment, args.status, args.deployment_result
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
