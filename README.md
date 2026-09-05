# LeadHunter SearXNG v2.0.0

Dedicated SearXNG backend for LeadHunter.

## Architecture

```text
Research Worker
      |
      | HTTPS + Basic Auth
      v
Render Web Service :10000
      |
      v
Auth Gateway
      |
      v
Official SearXNG :8080
      |
      v
Search engines
```

This implementation uses the official SearXNG container runtime. It does **not** run `python -m searx.webapp` and does not depend on an obsolete internal entrypoint path.

The free Render deployment uses a small Basic-Auth gateway because Render private services are not available on the free plan. The gateway exposes only `/healthz` without credentials and proxies authenticated GET requests to local SearXNG.

## Deploy

1. Deploy this repository as `leadhunter-searxng` in Singapore.
2. Let Render generate `SEARXNG_SECRET` and `SEARX_AUTH_PASSWORD`.
3. Check `/healthz`.
4. Test JSON search:

```bash
curl -u leadhunter:YOUR_PASSWORD \
  "https://YOUR-SEARXNG.onrender.com/search?q=dentist+Indore&format=json&language=en"
```

Expected: HTTP 200 with a JSON `results` array.

5. Put the Render URL and generated password into the Research Worker environment.

## Later private deployment

On a paid Render plan, this can be converted to `type: pserv` and the Research Worker can use the internal Render hostname. The SearXNG configuration itself remains the same.

Never commit the generated password to GitHub.
