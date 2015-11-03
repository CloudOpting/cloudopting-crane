# CloudOpting-Crane

This module provides a REST API that makes easy to build services with [Puppet](https://puppetlabs.com/) and [Docker](https://www.docker.com/).

It takes as input some files like puppetfiles, puppet manifests, dockerfiles and docker-compose files and builds a container infrastructure which can be deployed in remote machines (also using the API).

It uses several docker components: host, builder, registry, [swarm](https://github.com/docker/swarm) and [compose](https://github.com/docker/compose). Also puppet tools like the puppet agent itself and [r10k](https://github.com/puppetlabs/r10k).

## Components

Crane runs in several docker containers.

![Module diagram](/docs/resources/diagram.png)

- _commander_: contains the application which control all the logic (controllers) and a micro web server with the REST API (and a nice Swagger UI). 'Temp. storage' is a volume from this container and stores temporal files that the API receives (manifests, Dockerfiles...) and another temporal information like logs and another files useful for debuging.
- _redis_: container that runs an standalone redis. This __redis__ is used as context information storage for the __commander__ app. It allows the __commander__ to restart, go down and even upgrade maintaining the status. This __redis__ can be disabled leaving __commander__ using a filesystem type datastore.
- _docker-engine_: this container provides an interface for a docker-engine. This docker-engine runs in the host but with a separate namespace. This is used for building images.
- _docker-registry_: container that runs a private registry where base images and builded images will be stored.

## Requirements

- Docker 1.8 or superior
- Docker-compose 1.4 or superior
- OpenSSL

## How to deploy CloudOpting-Crane

### Step 1: get the certificates

Generate some self-signed certificates needed for the communication between components and with external elements. Just execute the script:

```
./genCerts.sh
```

This will generate several `certs` folders (one in each component) with the needed certificates.

These can be replaced with certificates obtained in other ways.

### Step 2: run it!

Type:

```
docker-compose -f <environment>.yml up
```

and docker-compose will build and run all the components.

Replace `<environment>` with `development`, `production` or `test`.


## Basic usage

### Launch crane

With the steps above.

### Interact with the API

You can use your favourite browser to navigate to `http://127.0.0.1:8888`. It will show a _swagger UI_ interface with all the API specification.

## On the desk

__Working on__
- Multihost swarm

__Issues__
- Nothing serious.

## Roadmap

- General refactoring
- Distributed building
- Docker-swarm complete support
  - customize hardware requirements by container with tags
- Update services on-the-fly
- Manage network parameters

## Tests: How to run the tests

Execute the script `runTests.sh`. You will need root permissions because it deletes files created by containers that runs as root.
