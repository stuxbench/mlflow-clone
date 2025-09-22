#!/usr/bin/env python3
"""
Test script to verify host header validation in MLflow server health endpoint.
"""

import os
import sys
import subprocess
import requests
import time
import threading
from contextlib import contextmanager


def test_host_validation():
    """Test the host header validation implementation."""

    # Test cases: (host_header, expected_status_code, description)
    test_cases = [
        # Valid cases
        ("localhost", 200, "Valid localhost"),
        ("127.0.0.1", 200, "Valid IP address"),
        ("localhost:5000", 200, "Valid localhost with port"),
        ("127.0.0.1:5000", 200, "Valid IP with port"),

        # Invalid cases
        ("evil.com", 400, "Invalid external domain"),
        ("attacker.com:80", 400, "Invalid external domain with port"),
        ("", 400, "Empty host header"),
        ("malicious-site.net", 400, "Malicious domain"),
    ]

    print("Testing host header validation for MLflow /health endpoint...")
    print("=" * 60)

    # Start MLflow server in background
    def start_server():
        os.environ["PYTHONPATH"] = "/home/evan/projects/spar/mlflow"
        subprocess.run([
            sys.executable, "-m", "mlflow.server",
            "--host", "127.0.0.1",
            "--port", "5000"
        ], capture_output=True)

    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Wait for server to start
    time.sleep(3)

    base_url = "http://127.0.0.1:5000"

    try:
        # Test each case
        for host_header, expected_status, description in test_cases:
            try:
                headers = {"Host": host_header} if host_header else {}
                response = requests.get(f"{base_url}/health", headers=headers, timeout=5)

                if response.status_code == expected_status:
                    status = "✓ PASS"
                else:
                    status = f"✗ FAIL (expected {expected_status}, got {response.status_code})"

                print(f"{status}: {description} - Host: '{host_header}'")

            except requests.exceptions.RequestException as e:
                print(f"✗ ERROR: {description} - {e}")

    except Exception as e:
        print(f"Test setup error: {e}")
    finally:
        # Clean up
        try:
            requests.get(f"{base_url}/health", timeout=1)
        except:
            pass

    print("=" * 60)
    print("Host header validation test completed!")


if __name__ == "__main__":
    test_host_validation()