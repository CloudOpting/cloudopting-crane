FROM ubuntu:12.04
MAINTAINER Jose Fuentes <jfuentes@wtelecom.es>

RUN apt-get -y update && apt-get -y install ruby
RUN apt-get install -y puppet

VOLUME containerLogs /tmp/logs

ADD modules /tmp/modules
ADD images/example/manifest.pp /tmp/manifest.pp

RUN puppet apply --modulepath=/tmp/modules /tmp/manifest.pp
