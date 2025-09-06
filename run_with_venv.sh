#!/bin/bash
# Script to run any command with the Walls virtual environment activated
# Usage: ./run_with_venv.sh <command>
# Example: ./run_with_venv.sh python -m radio_player.cli search --tag jazz

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Virtual environment not found at $VENV_PATH"
    echo "Please create the virtual environment first:"
    echo "  python -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    exit 1
fi

if [ $# -eq 0 ]; then
    echo "Usage: $0 <command>"
    echo "Example: $0 python -m radio_player.cli search --tag jazz"
    exit 1
fi

echo "🐍 Activating virtual environment..."
source "$VENV_PATH/bin/activate"

echo "▶️  Running: $*"
cd "$SCRIPT_DIR"
exec "$@"