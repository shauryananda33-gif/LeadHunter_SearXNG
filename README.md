# LeadHunter Render SearXNG — FULL FIX v1.1

This replaces the previous broken Render package.

## What was fixed

- Removed Python `crypt` completely.
- No bcrypt/htpasswd generation.
- No second proxy service.
- Render supplies `SEARXNG_SECRET` automatically.
- Render supplies a generated `SEARX_AUTH_PASSWORD` automatically.
- The gateway uses standard-library Basic Auth.
- SearXNG runs internally on port 8080.
- Render exposes only the authenticated gateway on `$PORT`.
- `/healthz` does not require authentication.
- JSON search remains enabled.

## Deploy

Push the repository contents to GitHub and redeploy the Render Blueprint.

The root must contain:

    render.yaml
    Dockerfile
    entrypoint.sh
    gateway.py
    searxng/settings.yml

Render will create:

    SEARXNG_SECRET
    SEARX_AUTH_USER
    SEARX_AUTH_PASSWORD

## Important: retrieving the generated password

Because `render.yaml` now uses `generateValue: true`, Render owns the generated
password. Open the service's Environment page and copy the generated
`SEARX_AUTH_PASSWORD`.

Do NOT invent another password in the Research Worker.

## Health test

Open:

    https://YOUR-SERVICE.onrender.com/healthz

Expected:

    {"ok":true,"service":"leadhunter-searxng","status":"healthy"}

## Search test

Use Basic Auth:

    curl -u leadhunter:YOUR_GENERATED_PASSWORD       "https://YOUR-SERVICE.onrender.com/search?q=dentist+Indore&format=json&language=en"

Expected: HTTP 200 and JSON containing `results`.

## Connect Research Worker

Only after the search test succeeds, set on the Research Worker:

    SEARXNG_URL=https://YOUR-SERVICE.onrender.com
    SEARXNG_AUTH_USER=leadhunter
    SEARXNG_AUTH_PASSWORD=THE_RENDER_GENERATED_PASSWORD

Then redeploy the Research Worker.

## Production note

This Render deployment is for proving the research/search architecture without
AWS. Render Free services may spin down when idle, and upstream search engines
can still impose rate limits. Once the worker is proven, we can move only the
search backend to better infrastructure without changing the worker API.
