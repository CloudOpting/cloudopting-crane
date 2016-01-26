import settings
import os

from controllers import errors
from toolbox import docker, files

def purge(datastore):
    '''
    Remove all the images, contexts, compositions, etc. Use carefully.
    '''
    try:
        status = {'status':'', 'description':''}
        # Purge docker
        docker.purge()

        # Purge filesystem
        try:
            files.purgeWorkdir()
        except:
            status['description']+="Can't remove files. "

        # Purge datastore
        try:
            datastore.clear()
        except:
            status['description']+="Can't clear datastore. "


        # Check response
        if status['description']=='':
            status['status']='finished'
            status['description']='Operation finished succefully'
        else:
            status['status']='incomplete'

        return status
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def getAllTokens(datastore):
    '''
    Get all tokens in datastore
    '''
    try:
        content = {}
        # get tokens from datastore
        try:
            content = datastore.getTokens()
        except:
            raise errors.ControllerError("Error in datastore.")

        return content
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def getDockerInfo(endpoint):
    '''
    Retrieve docker system information
    '''
    try:
        dk = docker.dockerClient(base_url=endpoint, cert_path=settings.DK_DEFAULT_MASTER_CLIENT_CERTS)
        return docker.dockerInfo(dk)
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
