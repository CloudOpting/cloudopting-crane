#!/bin/sh

set -e

# Copy registry CA cert
mkdir -p /etc/docker/certs.d/coregistry:5000
cp /var/lib/coengine/certs/registry-ca.crt /etc/docker/certs.d/coregistry:5000/ca.crt

if [ "$#" -eq 0 -o "${1:0:1}" = '-' ]; then
	set -- docker daemon \
		--host=unix:///var/run/docker.sock \
		--host=tcp://0.0.0.0:$PORT \
		--storage-driver=vfs $DOCKER_DAEMON_ARGS \
		"$@"
fi

if [ "$1" = 'docker' -a "$2" = 'daemon' ]; then
	# if we're running Docker, let's pipe through dind
	# (and we'll run dind explicitly with "sh" since its shebang is /bin/bash)
	set -- sh "$(which dind)" "$@"
fi

exec "$@"
