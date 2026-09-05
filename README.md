# LeadHunter SearXNG — Render v1

A temporary private-ish SearXNG service for the LeadHunter Research Worker.

## Architecture

Render Research Worker
        |
        | HTTPS + Basic Auth
        v
LeadHunter SearXNG Render service
        |
        v
SearXNG
        |
        +-- Google
        +-- Bing
        +-- Brave
        +-- DuckDuckGo
        +-- Mojeek
        +-- Startpage
        +-- Qwant

## Deploy on Render

1. Push this folder to a new GitHub repository.
2. In Render choose New -> Blueprint.
3. Connect the repository.
4. Render reads `render.yaml`.
5. Set `SEARX_AUTH_PASSWORD` to a long random password when prompted.
6. Deploy.

The generated `SEARXNG_SECRET` is supplied automatically by Render.

## Test

Health endpoint:

    https://YOUR-SERVICE.onrender.com/healthz

It should return:

    {"ok":true,"service":"leadhunter-searxng","status":"healthy"}

Search test:

    curl -u leadhunter:YOUR_PASSWORD       "https://YOUR-SERVICE.onrender.com/search?q=dentist+Indore&format=json&language=en"

A successful response should contain a `results` array.

## Connect Research Worker

Set these Render environment variables on the Research Worker:

    SEARXNG_URL=https://YOUR-SERVICE.onrender.com
    SEARXNG_AUTH_USER=leadhunter
    SEARXNG_AUTH_PASSWORD=YOUR_PASSWORD

Then redeploy the Research Worker.

## Important

This is a testing architecture, not the final production search infrastructure.

Render Free services can spin down when idle and public Render IPs are not dedicated.
The purpose here is to prove the LeadHunter research pipeline and search integration
without AWS.

Do not connect LeadHunter production until the worker's `/serp` endpoint returns
real results consistently.

If this service also receives HTTP 429 from upstream search engines, that is an
upstream-engine rate limit rather than the previous public-SearXNG-instance
rate-limit problem. We can then tune engine selection/query pacing or move only
the search backend to a more suitable host later.
