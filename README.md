# cloudopting-crane

This module provides a REST API that makes easy to build services with [Puppet](https://puppetlabs.com/) and [Docker](https://www.docker.com/).

It takes as input some files like puppetfiles, puppet manifests, dockerfiles and docker-compose files and builds a container infraestructure which can be deployed in remote machines (also using the API).

It uses several docker components: host, builder, registry, [swarm](https://github.com/docker/swarm) and [compose](https://github.com/docker/compose). Also puppet tools like the puppet agent itself and [r10k](https://github.com/puppetlabs/r10k).

![Module diagram](/readmeResources/diagram.png)



## On the desk

__Done__
- Dockerized environment for development
- Build puppet contexts from puppetfile
- Build containers from Dockerfile + puppet manifest
- Start services from docker-compose.yml
- Flexible data storage support (local-dict/filesystem/redis)

__Working on__
- Docker registry support (push and pull)
- Start services from docker-compose.yml (importing modules from docker-compose application)
- Deploy on remote host support
- Swarm support

## Roadmap

- Distributed building
- Docker-swarm complete support
  - add nodes to the cluster dynamically
  - customize hardware requirements by container
- Update services on-the-fly
- Manage network parameters
- Monitoring
