FROM ubuntu:14.04

# Install Docker
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y apt-transport-https
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
RUN mkdir -p /etc/apt/sources.list.d
RUN echo deb https://apt.dockerproject.org/repo ubuntu-trusty main > /etc/apt/sources.list.d/docker.list
RUN apt-get update -qq
RUN apt-get install -y --force-yes -q docker-engine
COPY launch.sh /root/launch.sh
RUN chmod +x /root/launch.sh

# Cleaning
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /root/
CMD ./launch.sh
