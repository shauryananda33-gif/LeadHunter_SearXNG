# LeadHunter Render SearXNG — FULL REBUILD v1.2

This is a complete replacement for v1.0/v1.1.

## Root cause fixed

The previous builds directly executed:

    python3 -m searx.webapp

That bypassed the official SearXNG container runtime and caused:

    ModuleNotFoundError: No module named 'msgspec'

This version does NOT do that.

It uses the official SearXNG container entrypoint:

    /usr/local/searxng/dockerfiles/docker-entrypoint.sh

The official runtime starts SearXNG using the dependencies and application
server included by the official image.

The official SearXNG container is based on the project's current container
runtime rather than treating the source package as a standalone Python module.

## Architecture

Internet
   |
Render public HTTPS
   |
authenticated gateway
   |
SearXNG internal :8080
   |
search engines

Only the gateway listens on Render's `$PORT`.

## Environment

Render creates automatically:

    SEARXNG_SECRET
    SEARX_AUTH_PASSWORD

and sets:

    SEARX_AUTH_USER=leadhunter

## Deployment

Replace the entire repository with this package.

The root must be:

    render.yaml
    Dockerfile
    start.sh
    gateway.py
    searxng/settings.yml

Then deploy the Render Blueprint.

## Test 1: health

Open:

    https://YOUR-SERVICE.onrender.com/healthz

Expected:

    {"ok":true,"service":"leadhunter-searxng","status":"healthy"}

## Test 2: authenticated JSON search

Use the generated Render password:

    curl -u leadhunter:YOUR_PASSWORD       "https://YOUR-SERVICE.onrender.com/search?q=dentist+Indore&format=json&language=en"

Expected:

    HTTP 200

and JSON containing:

    "results": [...]

## Test 3: Research Worker

Only after Test 2 succeeds, set on the Research Worker:

    SEARXNG_URL=https://YOUR-SERVICE.onrender.com
    SEARXNG_AUTH_USER=leadhunter
    SEARXNG_AUTH_PASSWORD=THE_RENDER_GENERATED_PASSWORD

Then redeploy the Research Worker and test /serp.

## Important

Do not modify LeadHunter production until the Research Worker returns real
search results.

This Render setup is intended to prove the architecture without AWS. Render
Free services can sleep when idle and search engines can still rate-limit
upstream traffic, so it is not being treated as final search infrastructure.
