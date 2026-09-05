#!/bin/sh
set -eu

: "${SEARXNG_SECRET:?SEARXNG_SECRET is required}"
: "${SEARX_AUTH_USER:?SEARX_AUTH_USER is required}"
: "${SEARX_AUTH_PASSWORD:?SEARX_AUTH_PASSWORD is required}"

export SEARXNG_SECRET

/usr/local/searxng/entrypoint.sh &
SEARX_PID=$!

ready=0
for _ in $(seq 1 90); do
    if wget -q -O /dev/null http://127.0.0.1:8080/healthz 2>/dev/null; then
        ready=1
        break
    fi
    if ! kill -0 "$SEARX_PID" 2>/dev/null; then
        wait "$SEARX_PID"
        exit 1
    fi
    sleep 1
done

if [ "$ready" -ne 1 ]; then
    echo "SearXNG did not become ready." >&2
    kill "$SEARX_PID" 2>/dev/null || true
    exit 1
fi

exec python3 /gateway.py
