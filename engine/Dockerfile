FROM docker:1.9.1-dind

COPY ./dockerd-entrypoint.sh /usr/local/bin/dockerd-entrypoint.sh

VOLUME /var/lib/docker
EXPOSE 4243

ENTRYPOINT ["/usr/local/bin/dockerd-entrypoint.sh"]
CMD []
