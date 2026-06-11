#!/bin/bash

python scripts/add_tasks_from_json.py

echo "Starting application..."
exec "$@"