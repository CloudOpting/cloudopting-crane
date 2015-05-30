# cloudopting-crane
The module that deals with docker operations: containers building, swarm clustering and compose orchestration.

![Module diagram](/readmeResources/diagram.png)

[Description under construction]

## On the desk

__Done__
- Dockerized environment for development
- API skell and definition (live swagger ui client)
- Flexible data storage support (local-dict/filesystem/redis)

__Working on__
- Build puppet contexts from puppetfile
- Build containers from Dockerfile
- Build containers from Dockerfile + puppet manifest
- Docker registry support (push and pull)
- Start services from docker-compose.yml (importing modules from docker-compose application)
- Configuration files


## Roadmap

- Distributed building
- Docker-swarm complete support
  - add nodes to the cluster dynamically
  - customize hardware requirements by container
- Update services on-the-fly
- Manage network parameters
- Monitoring
