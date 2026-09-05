#!/bin/sh
set -eu

: "${SEARXNG_SECRET:?SEARXNG_SECRET is required}"
: "${SEARX_AUTH_USER:?SEARX_AUTH_USER is required}"
: "${SEARX_AUTH_PASSWORD:?SEARX_AUTH_PASSWORD is required}"

# Put the Render-generated secret into SearXNG configuration.
sed -i "s|LEADHUNTER_SEARX_SECRET|${SEARXNG_SECRET}|g" /etc/searxng/settings.yml

# Start SearXNG using the official image entrypoint.
# This is critical: the official entrypoint configures and launches the
# Granian runtime with all dependencies included in the image.
if [ -x /usr/local/searxng/dockerfiles/docker-entrypoint.sh ]; then
    /usr/local/searxng/dockerfiles/docker-entrypoint.sh &
else
    echo "ERROR: official SearXNG docker-entrypoint.sh was not found."
    exit 1
fi

SEARX_PID=$!

# Wait for the internal SearXNG HTTP server.
i=0
while [ "$i" -lt 60 ]; do
    if wget -q -O /dev/null "http://127.0.0.1:8080/" 2>/dev/null; then
        echo "SearXNG internal server is ready."
        break
    fi

    if ! kill -0 "$SEARX_PID" 2>/dev/null; then
        echo "ERROR: SearXNG process exited during startup."
        wait "$SEARX_PID"
        exit 1
    fi

    i=$((i + 1))
    sleep 1
done

if ! wget -q -O /dev/null "http://127.0.0.1:8080/" 2>/dev/null; then
    echo "ERROR: SearXNG did not become ready within 60 seconds."
    exit 1
fi

exec python3 /gateway.py
