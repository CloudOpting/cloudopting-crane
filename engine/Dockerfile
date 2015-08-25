FROM ubuntu:14.04

# Install Docker
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
RUN mkdir -p /etc/apt/sources.list.d
RUN echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
RUN apt-get update
RUN apt-get install -y --force-yes -q docker-engine

# Configuring certificates and options

## Certificates can be generated with the 'genCerts.sh' in the root of this repository.
COPY ./certs/ca.pem /root/.docker/ca.pem
COPY ./certs/server-cert.pem /root/.docker/cert.pem
COPY ./certs/key.pem /root/.docker/key.pem

#COPY ./docker-engine.conf /etc/default/docker

# Cleaning
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#CMD docker --tlsverify -H=unix:///var/run/docker.sock -H=0.0.0.0:4243 --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem
