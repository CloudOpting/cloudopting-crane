# web service settings

WS_BIND_IP = '0.0.0.0'
"""Host ip to bind"""

WS_BIND_PORT = 8888
"""Port to bind"""

# datastore settings

DS_TYPE = 'filesystem'
""" Determine the type of the datastore. 'simple' is for a volatile dictionary, 'filesystem' is for persistent filesystem storage. 'redis' is for a redis storage. """

DS_FILESYSTEM_DIR = '/var/crane/datastore'
""" In case of 'filesystem' datastore, directory that store datastore.  """

DS_REDIS_HOST = ''
""" In case of 'redis' datastore, host that hosts the redis server. """

DS_REDIS_PORT = 6379
""" In case of 'redis' datastore, port where the redis server will be listening. """

DS_REDIS_PASSWORD = ''
""" In case of 'redis' datastore, password for server. """

DS_REDIS_DB = 0
""" In case of 'redis' datastore, redis DB. By default 0. """

# filesystem settings

FS_ROOT = '/var/crane/'
"""Root path for the application. Must ends in '/'"""

FS_BUILDS = FS_ROOT + 'builds/'
"""Path where the contexts and builds will be created. Must ends in '/'."""

FS_COMPOSITIONS = FS_ROOT + 'compositions/'
"""Path where the compositions will be created. Must ends in '/'."""

FS_DEF_PUPPETFILE = 'Puppetfile'
"""Default name for puppetfile"""

FS_DEF_DOCKERFILE = 'Dockerfile'
"""Default name for dockerfile"""

FS_DEF_PUPPETMANIFEST = 'manifest.pp'
"""Default name for puppet manifest"""

FS_DEF_COMPOSEFILE = 'docker-compose.yml'
"""Default name for docker compose yaml file"""

FS_DEF_CONTEXT_LOG = 'context.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_ERR_LOG = 'context_err.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_PID = 'pid'
"""Default name for the file that stores PID of the build context process"""

FS_DEF_DOCKER_IMAGES_FOLDER = 'images'
"""Default name for the folder which contains the images inside a context"""

FS_DEF_DOCKER_BUILD_LOG = 'build.log'
"""Default name for the log of the docker build process"""

FS_DEF_DOCKER_BUILD_ERR_LOG = 'build_err.log'
"""Default name for the log of the docker build process"""

FS_DEF_DOCKER_BUILD_PID = 'build_pid'
"""Default name for the file that stores PID of the docker build process"""

FS_DEF_DOCKER_COMPOSE_LOG = 'compose.log'
"""Default name for the log of docker compose"""

FS_DEF_DOCKER_COMPOSE_PID = 'compose_pid'
"""Default name for the file that stores PID of the docker compose process"""

# Docker host
DK_DEFAULT_BUILD_HOST = "unix:///var/run/docker.sock"
"""Default docker host where images will be built"""
