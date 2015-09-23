#!/bin/bash

FOLDER=${PWD##*/}
PREFIX=$(echo  "${FOLDER//-}" | awk '{print tolower($0)}')

# Remove previous containers if any
docker rm -f $(PREFIX)_registry_1 $(PREFIX)_engine_1 $(PREFIX)_redis_1 $(PREFIX)_commander_1 $(PREFIX)_testrunner_1 $(PREFIX)_emulatedhost_1

# Launch test composition
docker-compose -f ./test.yml up
