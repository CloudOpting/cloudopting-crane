import os
import settings
import subprocess
from threading import Thread

from controllers import errors
from fileUtils import createFile

def checkPuppetfile(token):
    '''
    Checks puppefile syntax. Returns True if correct syntax or the error if not.
    '''
    command = 'cd ' + os.path.join(settings.FS_BUILDS, token) + ' && r10k puppetfile check'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    response = ''
    for line in p.stdout.readlines():
        response+=line+os.linesep

    retval = p.wait()

    if retval == 0:
        return True
    else:
        return response



def buildContext(token):
    '''
    Creates a context in the filesystem ('/var/builder/contexts/<contextToken>'),
    stores the puppetfile and downloads the puppet modules. It is asynchronous, so it returns nothing.
    '''
    def buildThread():
        cwd =  os.path.join(settings.FS_BUILDS, token)
        command = 'r10k puppetfile install 1> '+ settings.FS_DEF_CONTEXT_LOG +' 2> '+ settings.FS_DEF_CONTEXT_ERR_LOG
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        createFile(os.path.join(cwd, settings.FS_DEF_CONTEXT_PID), str(p.pid))

        retval = p.wait()

    thread = Thread(target = buildThread)
    thread.start()


def isBuildingContextRunning(token):
    '''
    Checks if the build context process is still running. Returns True if the process still runs and False if the process is not running.
    '''
    pidpath = os.path.join(settings.FS_BUILDS, token)
    pidpath = os.path.join(pidpath, settings.FS_DEF_CONTEXT_PID)
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

def getBuildingErrors(token):
    '''
    Retrieve errors in error building log. None if no errors.
    '''
    path = os.path.join(settings.FS_BUILDS, token)
    path = os.path.join(path, settings.FS_DEF_CONTEXT_ERR_LOG)
    if os.stat(path).st_size == 0:
        return None
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def getBuildingLog(token):
    '''
    Retrieve standard building log.
    '''
    path = os.path.join(settings.FS_BUILDS, token)
    path = os.path.join(path, settings.FS_DEF_CONTEXT_LOG)
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def stopBuildingContext(token):
    '''
    Stops the build process. Return True if could stop and False it not.
    '''
    pidpath = os.path.join(settings.FS_BUILDS, token)
    pidpath = os.path.join(pidpath, settings.FS_DEF_CONTEXT_PID)
    file = open(pidpath, 'r')
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 9)
            return True
        except OSError:
            return False
