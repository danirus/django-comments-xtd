#!/usr/bin/env bash

# I use pkill down here, and as it can return 1 when no process matches
# the pid given in the file, I disable the `set -e` in this line below.
# Otherwise `pkill -F runserver.pid`, when returning 1, would exit
# immediately.
# set -e  # If a cmd exits with non-zero status, exit immediately.

# Get the script's path.
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" &>/dev/null && pwd)

# Change CWD to the resolved directory.
cd "$SCRIPT_DIR" || {
    echo "Error: Failed to change directory to $SCRIPT_DIR" >&2
    exit 1
}

if [ -f runserver.pid ]; then
    pkill -F runserver.pid
    rm runserver.pid
fi
exit 0
