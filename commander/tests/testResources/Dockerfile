FROM cloudopting/ubuntubase
MAINTAINER Jose Fuentes <jfuentes@wtelecom.es>

VOLUME containerLogs /tmp/logs

ADD manifest.pp /tmp/manifest.pp

RUN puppet apply /tmp/manifest.pp
