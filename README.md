# CloudOpting-Crane

This module provides a REST API that makes easy to build services with [Puppet](https://puppetlabs.com/) and [Docker](https://www.docker.com/).

It takes as input some files like puppetfiles, puppet manifests, dockerfiles and docker-compose files and builds a container infraestructure which can be deployed in remote machines (also using the API).

It uses several docker components: host, builder, registry, [swarm](https://github.com/docker/swarm) and [compose](https://github.com/docker/compose). Also puppet tools like the puppet agent itself and [r10k](https://github.com/puppetlabs/r10k).

![Module diagram](/readmeResources/diagram.png)

## How to deploy CloudOpting-Crane

### Requirements

- Ruby
- [r10k](https://github.com/puppetlabs/r10k)
- [docker](https://docs.docker.com/installation/)
- [docker-compose](https://docs.docker.com/compose/#installation-and-set-up)
- Python 2.7
- [Flask](http://flask.pocoo.org/)
- [Flask-restplus](https://github.com/noirbizarre/flask-restplus)
- [Flask-cache](https://pythonhosted.org/Flask-Cache/)
- [Docker-py](https://github.com/docker/docker-py)

### Steps (CentOS)

- Install r10k

 `yum install ruby`

 `gem install r10k`

- Install docker

  In centos 7: `yum install docker`

  In centos 6.5: [see this](https://docs.docker.com/installation/centos/)

- Install pip (helps to install docker-compose and python needed libraries):

  `curl "https://bootstrap.pypa.io/get-pip.py" -o "get-pip.py"`
  `python get-pip.py`

- Clone repository where you want:

  `git clone https://github.com/CloudOpting/cloudopting-crane`

- Change directory to the project root:

  `cd cloudopting-crane`

- Install needed python libraries including docker-compose (listed in file `install/requirements.txt`):

  `pip install -r install/requirements.txt`


- Run commander REST API :

  `cd commander`

  `python commander.py`

## Alternative intallation methods (useful for development and testing)

- Dockerized: take a look into `install/dockerization/`. More detailed instructions will come.

- Vagrant: a vagrant recipe will be available soon.


### Configuration

#### Docker

- __Non-root client__: the docker daemon interact with the docker client throw a unix socker owned by root. This mean that by default the docker client has to be run as root as well. To avoid this it is possible to change the socket owner group to 'docker' and execute the client with a user also in the 'docker' group. This are the steps:

  - Create 'docker' group: `groupadd docker`
  - Add root user to group: `gpasswd -a root docker`
  - Add the user who will execute the client to group: `gpasswd -a crane docker`
  - Apply changes in group: `newgrp docker`
  - Restart docker daemon: `service docker restart`

#### System

- __Firewalld__: if you use _firewalld_ (centos) you have to assure that _docker daemon_ is launched after _firewalld daemon_. By default this works this way but take into account you will need to restart the _docker daemon_ each time _firewalld_ is restarted.

- __Filesystem permissions__: the commander process (and others launched by this) will use the filesystem to persist and exchange some data. By default it uses the root folder `/var/crane`, but it can be changed in the file `settings.py`. Assure the user who runs the commander process has read and write permissions to that directory or the directory you choose. It is possible to create manually the `/var/crane` directory and give write permissions only for the `crane` folder.

#### Commander

- __Bind ip__: in `settings.py`, the `WS_BIND_IP` parameter change the bind address for the REST API. `0.0.0.0` bind to any address in the machine, `127.0.0.1` bind only localhost.

- __Bind port__: in `settings.py`, the `WS_BIND_PORT` parameter change the port where the REST API will be listening.

- __DEBUG mode__: If the environment variable `DEBUG` is defined as `True` the process will run in debug mode and it will return debug information in the requests when something fails. It is not recomended for production use.

- __Context storage__: The commander process uses an abstract datastore in order to maintain the context information. By default this is configured as a internal and volatile dictionary. It is possible to select also a filesystem based storage or a redis server ('DS_TYPE' in `settings.py`).

## Basic usage

### Launch the server

Execute 'python commander.py' in '/commander' with an user allowed to interact with the docker daemon.

### Interact with the API

You can use your favourite browser to navigate to `http://127.0.0.1:8888`. It will show a _swagger UI_ interface with all the API specification.

## On the desk

__Done__
- Dockerized environment for development
- Build puppet contexts from puppetfile
- Build containers from Dockerfile + puppet manifest
- Start services from docker-compose.yml
- Flexible data storage support (local-dict/filesystem/. Not redis for the moment).

__Working on__
- Docker registry support (push and pull)
- Substitute docker-compose calls for native python calls.
- Deploy on remote host support
- Cluster support: create a swarm cluster, deploy on swarm cluster

## Roadmap

- General refactoring
- Distributed building
- Docker-swarm complete support
  - add nodes to the cluster dynamically
  - customize hardware requirements by container
- Update services on-the-fly
- Manage network parameters
- Monitoring
