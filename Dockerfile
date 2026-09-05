FROM ghcr.io/searxng/searxng:2026.8.29-d226b78bc

USER root
COPY settings.yml /etc/searxng/settings.yml
COPY entrypoint.sh /entrypoint-leadhunter.sh
COPY gateway.py /gateway.py
RUN chmod +x /entrypoint-leadhunter.sh

EXPOSE 10000
ENTRYPOINT ["/entrypoint-leadhunter.sh"]
