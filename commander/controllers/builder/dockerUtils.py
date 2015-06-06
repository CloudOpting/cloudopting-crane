import os
import settings
import subprocess
from threading import Thread

from controllers import errors
from fileUtils import createFile

def buildImage(datastore, contextToken, imageName, imageToken, dockerClient=settings.DK_DEFAULT_BUILD_HOST):
    # launch build
    # TODO: replace commandline docker API with docker-py client
    def buildThread():
        cwd =  os.path.join(settings.FS_BUILDS, contextToken)
        cwd =  os.path.join(settings.FS_BUILDS, imageName)
        command = 'docker build -t '+ contextToken.lower() + '/'+ imageName.lower() +' . ' + '1> '+ settings.FS_DEF_DOCKER_BUILD_LOG +' 2> '+ settings.FS_DEF_DOCKER_BUILD_ERR_LOG
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        createFile(os.path.join(cwd, settings.FS_DEF_DOCKER_BUILD_PID), str(p.pid))

        retval = p.wait()

    thread = Thread(target = buildThread)
    thread.start()

def isDockerBuildRunning(contextToken, imageName):
    '''
    Checks if the docker build process is still running. Returns True if the process still runs and False if the process is not running.
    '''
    pidpath = os.path.join(settings.FS_BUILDS, contextToken)
    pidpath = os.path.join(pidpath, imageName)
    pidpath = os.path.join(pidpath, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(pidpath, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            pass
    return False


def getBuildErrors(contextToken, imageName):
    '''
    Retrieve errors in error building log. None if no errors.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)
    if os.stat(path).st_size == 0:
        return None
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def getBuildLog(contextToken, imageName):
    '''
    Retrieve standard building log.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_LOG)
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def stopBuild(contextToken, imageName):
    '''
    Stops the build process. Return True if could stop and False it not.
    '''
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(pidpath, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 9)
            return True
        except OSError:
            return False
