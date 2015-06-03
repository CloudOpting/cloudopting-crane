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

FS_DEF_CONTEXT_LOG = 'context.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_ERR_LOG = 'context_err.log'
"""Default name for the log of the build context process"""

FS_DEF_CONTEXT_PID = 'pid'
"""Default name for the file that stores PID of the build context process"""
