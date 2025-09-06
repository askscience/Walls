from __future__ import annotations

import argparse
import json
import socket
import sys
from typing import Any, Dict
from pathlib import Path
import tempfile
import os

# Ensure Walls root is on sys.path so we can import shared_server
THIS_FILE = os.path.abspath(__file__)
WALLS_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(THIS_FILE))))
if WALLS_ROOT not in sys.path:
    sys.path.insert(0, WALLS_ROOT)

from shared_server.client import send_command_to_app


def send(cmd: str, args: Dict[str, Any]) -> None:
    print(f"Sending command '{cmd}' with args: {args}")
    try:
        result = send_command_to_app("words", cmd, args)
        if result:
            if result.get('status') == 'success':
                print(f"✓ {result.get('message', 'Command executed successfully')}")
                if 'data' in result:
                    for key, value in result['data'].items():
                        print(f"  {key}: {value}")
            else:
                print(f"✗ {result.get('message', 'Command failed')}")
        else:
            print("✗ Failed to communicate with GUI application")
    except Exception as e:
        print(f"Failed to send command: {e}")


def repl() -> None:
    print("Words CLI interactive mode. Enter commands:")
    print("  set_text {text}")
    print("  insert_text {offset} {text}")
    print("  open {path}")
    print("  save {path}")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not line:
            continue
        parts = line.split(maxsplit=2)
        if not parts:
            continue
        cmd = parts[0]
        if cmd == "set_text" and len(parts) >= 2:
            send("set_text", {"text": parts[1] if len(parts) == 2 else parts[1] + (" " + parts[2] if len(parts) > 2 else "")})
        elif cmd == "insert_text" and len(parts) >= 3:
            try:
                offset = int(parts[1])
            except ValueError:
                print("offset must be integer")
                continue
            send("insert_text", {"offset": offset, "text": parts[2]})
        elif cmd == "open" and len(parts) >= 2:
            send("open", {"path": parts[1]})
        elif cmd == "save" and len(parts) >= 2:
            send("save", {"path": parts[1]})
        else:
            print("Unknown or malformed command")


def main() -> None:
    parser = argparse.ArgumentParser(description="Words CLI - control the running GUI in real time")
    parser.add_argument("command", nargs="?", help="Command to send: set_text | insert_text | open | save")
    parser.add_argument("params", nargs=argparse.REMAINDER, help="Parameters for the command")
    args = parser.parse_args()

    if not args.command:
        # Interactive mode
        repl()
        return

    cmd = args.command
    if cmd == "set_text":
        text = " ".join(args.params)
        send("set_text", {"text": text})
    elif cmd == "insert_text":
        if len(args.params) < 2:
            print("Usage: insert_text <offset> <text>")
            sys.exit(1)
        offset = int(args.params[0])
        text = " ".join(args.params[1:])
        send("insert_text", {"offset": offset, "text": text})
    elif cmd == "open":
        if len(args.params) < 1:
            print("Usage: open <path>")
            sys.exit(1)
        send("open", {"path": args.params[0]})
    elif cmd == "save":
        if len(args.params) < 1:
            print("Usage: save <path>")
            sys.exit(1)
        send("save", {"path": args.params[0]})
    else:
        print("Unknown command")
        sys.exit(1)


if __name__ == "__main__":
    main()