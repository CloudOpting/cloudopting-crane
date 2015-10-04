#!/bin/bash

# Docker daemon (if docker-machine, boot2docker, or any not local)
export DOCKER_TLS_VERIFY=1;
export DOCKER_HOST=tcp://172.16.136.130:2376;
export DOCKER_CERT_PATH=/Users/jfc/.docker/machine/machines/dev-wts;
export DOCKER_MACHINE_NAME=dev-wts;

PWD=$(pwd)
FOLDER=${PWD##*/}
PREFIX=$(echo  "${FOLDER//-}" | awk '{print tolower($0)}')

# Remove previous containers if any
docker rm -f -v ${PREFIX}_registry_1 ${PREFIX}_engine_1 ${PREFIX}_redis_1 ${PREFIX}_commander_1 ${PREFIX}_testrunner_1 ${PREFIX}_emulatedhost_1

# Clean previous tests data
rm -rf ./commander/commander-data-tests
rm -rf ./registry/registry-data-tests

# Launch test composition
docker-compose -f ./test.yml up
