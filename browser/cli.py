#!/usr/bin/env python3
"""CLI for controlling the Browser app via shared_server."""

import sys
import os
import subprocess
import time
from shared_server.client import send_command_to_app, is_app_running, ServerClient

APP_NAME = "browser"


def _ensure_app_running(timeout: float = 15.0) -> bool:
    """Ensure the browser app is running; if not, start it and wait until it's ready."""
    if is_app_running(APP_NAME):
        return True
    # Start the browser shared server integration in background
    print("[browser.cli] Browser app is not running; starting it...")
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.devnull, 'w') as devnull:
        subprocess.Popen([sys.executable, "-m", "browser.shared_server_integration"], cwd=workspace_root, stdout=devnull, stderr=devnull)
    # Wait for readiness
    deadline = time.time() + timeout
    while time.time() < deadline:
        if is_app_running(APP_NAME):
            print("[browser.cli] Browser app is ready.")
            # Give the GUI event loop a brief moment to start processing events
            time.sleep(0.5)
            return True
        time.sleep(0.25)
    print("[browser.cli] Timed out waiting for browser app to start.")
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m browser.cli <command> [key=value ...]")
        sys.exit(1)

    command = sys.argv[1]
    args_list = sys.argv[2:]

    # Parse key=value args into dict; also allow positional as arg0, arg1, ...
    args = {}
    for i, arg in enumerate(args_list):
        if '=' in arg:
            k, v = arg.split('=', 1)
            args[k] = v
        else:
            args[f'arg{i}'] = arg

    if not _ensure_app_running():
        sys.exit(1)

    try:
        # Use a slightly longer timeout to account for first-command UI warm-up
        client = ServerClient(APP_NAME, timeout=15.0)
        resp = client.send_command(command, args)
        status = resp.get('status')
        message = resp.get('message', '')
        if status == 'success':
            print(f"success: {message}")
        else:
            print(f"error: {message}")
            if 'data' in resp:
                print(resp['data'])
    except Exception as e:
        print(f"error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()