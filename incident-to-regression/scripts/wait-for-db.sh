#!/usr/bin/env bash
# wait-for-db.sh

set -e

host="$1"
port="$2"
user="$3"
shift 3
cmd="$@"

echo "Waiting for PostgreSQL at $host:$port..."

# We attempt to use pg_isready if available
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if pg_isready -h "$host" -p "$port" -U "$user" >/dev/null 2>&1; then
        echo "PostgreSQL is ready!"
        exec $cmd
        exit 0
    fi
    echo "Attempt $attempt/$max_attempts: PostgreSQL is unavailable - sleeping"
    sleep 2
    attempt=$((attempt + 1))
done

echo "Error: PostgreSQL did not become ready in time"
exit 1
