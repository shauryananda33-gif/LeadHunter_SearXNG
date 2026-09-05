# Use the official SearXNG container and preserve its own runtime.
# The previous versions incorrectly called `python3 -m searx.webapp` directly,
# bypassing the dependencies/runtime prepared by the official image.
FROM ghcr.io/searxng/searxng:2026.8.29-d226b78bc

USER root

COPY searxng/settings.yml /etc/searxng/settings.yml
COPY gateway.py /gateway.py
COPY start.sh /start.sh

RUN chmod +x /start.sh

EXPOSE 10000

ENTRYPOINT ["/start.sh"]
