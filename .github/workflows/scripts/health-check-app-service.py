#!/usr/bin/env python3
"""
Health check for App Service deployment.
Verifies the app is responding and healthy.
"""

import argparse
import subprocess
import sys
import time
from datetime import UTC, datetime

import requests


def get_app_service_url(app_service_name, resource_group, slot=None):
    """Get the URL for an App Service."""

    cmd = ["az", "webapp", "show", "--name", app_service_name, "--resource-group", resource_group]

    if slot and slot != "production":
        cmd.extend(["--slot", slot])

    cmd.extend(["--query", "defaultHostName", "--output", "tsv"])

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        raise Exception(f"Failed to get app service URL: {result.stderr}")

    hostname = result.stdout.strip()
    return f"https://{hostname}"


def health_check(app_service_name, resource_group, slot, timeout=300):
    """Verify App Service is healthy and responding."""

    start_time = time.time()
    attempt = 0
    max_attempts = (timeout // 10) + 1

    # Get the app service URL
    try:
        app_url = get_app_service_url(app_service_name, resource_group, slot)
        print(f"🔍 Checking health: {app_url}\n")
    except Exception as e:
        print(f"⚠️ Could not determine app URL: {e}")
        return False

    while attempt < max_attempts:
        try:
            elapsed = time.time() - start_time
            attempt += 1

            print(f"[Attempt {attempt}] Health check ({elapsed:.0f}s elapsed)...")

            # Try health endpoint first
            try:
                response = requests.get(f"{app_url}/health", timeout=10, verify=False)

                if response.status_code == 200:
                    print("  ✓ Health endpoint returned 200")
                    return True
                else:
                    print(f"  ⚠ Health endpoint returned {response.status_code}")
            except requests.exceptions.RequestException:
                pass  # Try main endpoint instead

            # Try main app
            response = requests.get(app_url, timeout=10, verify=False)

            if response.status_code == 200:
                print("  ✓ App responding with 200")
                print("\n✅ Health check PASSED")
                print(f"   URL: {app_url}")
                print(f"   Slot: {slot}")
                print(f"   Time: {datetime.now(UTC).isoformat()}\n")
                return True
            else:
                print(f"  ⚠ App returned {response.status_code}")

        except requests.exceptions.Timeout:
            elapsed = time.time() - start_time
            if elapsed < timeout:
                print("  ⏳ Timeout (retrying in 10s)...")
                time.sleep(10)
            else:
                print("\n❌ Health check FAILED: Timeout")
                return False

        except Exception as e:
            elapsed = time.time() - start_time

            if elapsed < timeout:
                print(f"  ⓘ {e}")
                print(f"  ⏳ Retrying in 10s ({elapsed:.0f}s/{timeout}s)...")
                time.sleep(10)
            else:
                print(f"\n❌ Health check FAILED: {e}")
                return False


def main():
    parser = argparse.ArgumentParser(description="Health check for App Service")
    parser.add_argument("--app-service-name", required=True)
    parser.add_argument("--resource-group", required=True)
    parser.add_argument("--slot", default="production")
    parser.add_argument("--timeout", type=int, default=300)

    args = parser.parse_args()

    success = health_check(args.app_service_name, args.resource_group, args.slot, args.timeout)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
