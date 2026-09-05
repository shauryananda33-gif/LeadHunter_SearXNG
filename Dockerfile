FROM searxng/searxng:latest

USER root

COPY searxng/settings.yml /etc/searxng/settings.yml
COPY gateway.py /gateway.py
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 10000

ENTRYPOINT ["/entrypoint.sh"]
