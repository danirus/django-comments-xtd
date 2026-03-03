#!/usr/bin/env bash

set -e  # If a cmd exits with non-zero status, exit immediately.

# Get the script's path.
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" &>/dev/null && pwd)

# Change CWD to the resolved directory.
cd "$SCRIPT_DIR" || {
    echo "Error: Failed to change directory to $SCRIPT_DIR" >&2
    exit 1
}

pkill -F runserver.pid
rm runserver.pid
exit 0
