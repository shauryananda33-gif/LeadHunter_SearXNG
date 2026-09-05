#!/bin/sh
set -eu

: "${SEARXNG_SECRET:?SEARXNG_SECRET is required}"
: "${SEARX_AUTH_USER:?SEARX_AUTH_USER is required}"
: "${SEARX_AUTH_PASSWORD:?SEARX_AUTH_PASSWORD is required}"

# Inject the Render-provided secret into the SearXNG settings file.
sed -i "s|LEADHUNTER_SEARX_SECRET|${SEARXNG_SECRET}|g" /etc/searxng/settings.yml

# Start SearXNG in the background. The gateway is the only process exposed
# to Render's public port.
python3 -m searx.webapp &
SEARX_PID=$!

# Give SearXNG a moment to initialize before the gateway starts.
i=0
while [ "$i" -lt 30 ]; do
    if wget -q -O /dev/null "http://127.0.0.1:8080/" 2>/dev/null; then
        break
    fi
    if ! kill -0 "$SEARX_PID" 2>/dev/null; then
        echo "SearXNG exited during startup."
        wait "$SEARX_PID"
        exit 1
    fi
    i=$((i + 1))
    sleep 1
done

exec python3 /gateway.py
