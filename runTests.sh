#!/bin/bash
PWD=$(pwd)
FOLDER=${PWD##*/}
PREFIX=co

# Remove previous containers if any
docker rm -f -v ${PREFIX}_registry ${PREFIX}_engine ${PREFIX}_redis ${PREFIX}_commander ${PREFIX}_testrunner ${PREFIX}_emulatedhost

# Clean previous tests data
sudo rm -rf ./commander/commander-data-tests
sudo rm -rf ./registry/registry-data-tests

# Launch test composition
docker-compose -f ./test.yml up
