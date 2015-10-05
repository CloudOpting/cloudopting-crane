#!/bin/bash
PWD=$(pwd)
FOLDER=${PWD##*/}
PREFIX=$(echo  "${FOLDER//-}" | awk '{print tolower($0)}')

# Remove previous containers if any
docker rm -f -v ${PREFIX}_registry_1 ${PREFIX}_engine_1 ${PREFIX}_redis_1 ${PREFIX}_commander_1 ${PREFIX}_testrunner_1 ${PREFIX}_emulatedhost_1

# Clean previous tests data
sudo rm -rf ./commander/commander-data-tests
sudo rm -rf ./registry/registry-data-tests

# Launch test composition
docker-compose -f ./test.yml up
