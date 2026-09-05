#!/bin/sh
set -eu

: "${SEARXNG_SECRET:?SEARXNG_SECRET is required}"
: "${SEARX_AUTH_USER:?SEARX_AUTH_USER is required}"
: "${SEARX_AUTH_PASSWORD:?SEARX_AUTH_PASSWORD is required}"

# Generate a bcrypt htpasswd file for the small auth gateway.
# The gateway is intentionally implemented in Python so there is only one
# Render service and no second public proxy service to maintain.
python3 - <<'PY'
import os, crypt, pathlib

user = os.environ["SEARX_AUTH_USER"]
password = os.environ["SEARX_AUTH_PASSWORD"]

if not password:
    raise SystemExit("SEARX_AUTH_PASSWORD must not be empty")

hashed = crypt.crypt(password, crypt.mksalt(crypt.METHOD_BLOWFISH))
pathlib.Path("/etc/searxng/.auth").write_text(f"{user}:{hashed}\n")
PY

# SearXNG reads its secret from the settings file. Replace the placeholder
# without exposing the value in application logs.
sed -i "s|LEADHUNTER_SEARX_SECRET|${SEARXNG_SECRET}|g" /etc/searxng/settings.yml

exec python3 /gateway.py
