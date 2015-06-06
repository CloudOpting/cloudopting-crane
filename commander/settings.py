# web service settings

WS_BIND_IP = '0.0.0.0'
"""Host ip to bind"""

WS_BIND_PORT = 8888
"""Port to bind"""


# filesystem settings

FS_ROOT = '/var/crane/'
"""Root path for the application. Must ends in '/'"""

FS_BUILDS = FS_ROOT + 'builds/'
"""Path where the contexts and builds will be created. Must ends in '/'."""

FS_DEF_PUPPETFILE = 'Puppetfile'
"""Default name for puppetfile"""

FS_DEF_DOCKERFILE = 'Dockerfile'
"""Default name for dockerfile"""

FS_DEF_PUPPETMANIFEST = 'init.pp'
"""Default name for puppet manifest"""

FS_DEF_CONTEXT_LOG = 'context.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_ERR_LOG = 'context_err.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_PID = 'pid'
"""Default name for the file that stores PID of the build context process"""

FS_DEF_DOCKER_BUILD_LOG = 'build.log'
"""Default name for the log of the docker build process"""

FS_DEF_DOCKER_BUILD_ERR_LOG = 'build_err.log'
"""Default name for the log of the docker build process"""

FS_DEF_DOCKER_BUILD_PID = 'build_pid'
"""Default name for the file that stores PID of the docker build process"""

# Docker host
DK_DEFAULT_BUILD_HOST = "tcp://127.0.0.1:2375"
"""Default docker host where images will be built"""
