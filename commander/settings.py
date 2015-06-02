# web service settings

WS_BIND_IP = '0.0.0.0'
"""Host ip to bind"""

WS_BIND_PORT = 8888
"""Port to bind"""


# filesystem settings

FS_ROOT = '/var/crane/'
"""Root path for the application"""

FS_BUILDS = FS_ROOT + 'builds/'
"""Path where the contexts and builds will be created"""

FS_DEF_PUPPETFILE = 'Puppetfile'
"""Default name for puppetfile"""
