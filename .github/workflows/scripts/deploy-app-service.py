#!/usr/bin/env python3
"""
Deploy Docker image to Azure App Service.
Handles slot deployment for Blue-Green strategy.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import UTC, datetime


def deploy_to_app_service(app_service_name, resource_group, image_url, slot, acr_username, acr_password):
    """Deploy Docker image to App Service slot."""

    deployment_info = {
        "app_service_name": app_service_name,
        "resource_group": resource_group,
        "image_url": image_url,
        "slot": slot,
        "timestamp": datetime.now(UTC).isoformat(),
        "status": "pending",
    }

    try:
        print("🚀 Deploying image to App Service...")
        print(f"   App Service: {app_service_name}")
        print(f"   Resource Group: {resource_group}")
        print(f"   Slot: {slot}")
        print(f"   Image: {image_url}\n")

        # Update App Service with Docker image
        cmd = [
            "az",
            "webapp",
            "config",
            "container",
            "set",
            "--name",
            app_service_name,
            "--resource-group",
            resource_group,
            "--docker-custom-image-name",
            image_url,
            "--docker-registry-server-url",
            f"https://{image_url.split('/')[0]}",
            "--docker-registry-server-username",
            acr_username,
            "--docker-registry-server-password",
            acr_password,
            "--slot",
            slot,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise Exception(f"Azure CLI failed: {result.stderr}")

        print("✅ Docker image configured on App Service")

        # Wait for deployment to complete
        print(f"⏳ Waiting for App Service to restart ({slot} slot)...")

        # Note: Slot might already exist, so we just check status
        cmd_status = [
            "az",
            "webapp",
            "show",
            "--name",
            app_service_name,
            "--resource-group",
            resource_group,
            "--query",
            "state",
            "--output",
            "tsv",
        ]

        result = subprocess.run(cmd_status, capture_output=True, text=True, timeout=60)
        state = result.stdout.strip()

        deployment_info["status"] = "success"
        deployment_info["app_state"] = state
        deployment_info["deployment_time"] = datetime.now(UTC).isoformat()

        print("✅ Deployment completed")
        print(f"   App State: {state}\n")

        return deployment_info

    except Exception as e:
        deployment_info["status"] = "failed"
        deployment_info["error"] = str(e)
        print(f"❌ Deployment failed: {e}\n")
        raise


def main():
    parser = argparse.ArgumentParser(description="Deploy to App Service")
    parser.add_argument("--app-service-name", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--image-url", required=True)
    parser.add_argument("--slot", required=True)
    parser.add_argument("--output-file", default="deployment-result.json")

    args = parser.parse_args()

    # Verify ACR credentials are available
    acr_username = os.getenv("ACR_USERNAME")
    acr_password = os.getenv("ACR_PASSWORD")

    if not acr_username or not acr_password:
        print("❌ ACR_USERNAME and ACR_PASSWORD environment variables required", file=sys.stderr)
        sys.exit(1)

    try:
        result = deploy_to_app_service(
            args.app_service_name,
            args.resource_group,
            args.image_url,
            args.slot,
            acr_username,
            acr_password,
        )

        with open(args.output_file, "w") as f:
            json.dump(result, f, indent=2)

        sys.exit(0)

    except Exception as e:
        print(f"❌ Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
