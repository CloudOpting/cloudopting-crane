import os
import settings
import subprocess

from controllers import errors

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
    stores the puppetfile and downloads the puppet modules.
    '''
    # TODO: call r10k to deploy the puppetfile
    command = 'cd ' + os.path.join(settings.FS_BUILDS, token) + ' && r10k puppetfile check'
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
