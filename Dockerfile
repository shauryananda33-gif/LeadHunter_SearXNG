FROM searxng/searxng:latest

USER root

COPY searxng/settings.yml /etc/searxng/settings.yml
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

EXPOSE 8080

ENTRYPOINT ["/entrypoint.sh"]
