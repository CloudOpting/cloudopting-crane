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
