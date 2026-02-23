#!/usr/bin/env bash

set -e  # If a cmd exits with non-zero status, exit immediately.

# Get the script's path.
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR=$(cd "$(dirname "$SCRIPT_PATH")" &>/dev/null && pwd)

# Change CWD to the resolved directory.
cd "$SCRIPT_DIR" || {
  echo "Error: Failed to change directory to $SCRIPT_DIR." >&2
  exit 1
}

if [ -f "runserver.pid" ]; then
  echo "Error: runserver.pid already exists."
  exit 1
fi

rm db.sqlite3
source ../../venv/bin/activate
python manage.py migrate
python manage.py loaddata fixtures/sites.json
python manage.py loaddata fixtures/users.json
python manage.py loaddata fixtures/specs.json
nohup ./manage.py runserver localhost:8333 &>/dev/null &
echo $! > runserver.pid
exit 0
