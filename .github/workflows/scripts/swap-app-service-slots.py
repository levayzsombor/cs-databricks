#!/usr/bin/env python3
"""
Swap App Service deployment slots (Blue-Green deployment).
Safely switches production traffic to staging slot.
"""

import argparse
import subprocess
import sys
from datetime import UTC, datetime


def swap_slots(app_service_name, resource_group):
    """Swap App Service slots."""

    print("🔄 Swapping App Service slots...\n")
    print(f"   App Service: {app_service_name}")
    print(f"   Resource Group: {resource_group}\n")

    try:
        # Perform slot swap
        cmd = [
            "az",
            "webapp",
            "deployment",
            "slot",
            "swap",
            "--name",
            app_service_name,
            "--resource-group",
            resource_group,
            "--slot",
            "staging",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            raise Exception(f"Slot swap failed: {result.stderr}")

        print("✅ Slots swapped successfully")
        print("   Staging → Production\n")

        # Verify swap
        cmd_verify = [
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

        result = subprocess.run(cmd_verify, capture_output=True, text=True, timeout=60)
        state = result.stdout.strip()

        print(f"✅ App Service state: {state}")
        print(f"   Timestamp: {datetime.now(UTC).isoformat()}\n")

        return True

    except Exception as e:
        print(f"❌ Slot swap failed: {e}\n")
        raise


def main():
    parser = argparse.ArgumentParser(description="Swap App Service slots")
    parser.add_argument("--app-service-name", required=True)
    parser.add_argument("--resource-group", required=True)

    args = parser.parse_args()

    try:
        swap_slots(args.app_service_name, args.resource_group)
        sys.exit(0)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
