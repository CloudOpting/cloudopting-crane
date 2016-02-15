import settings
import os

from controllers import errors
from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from toolbox import docker
from toolbox import files

def newComposition(datastore, composefile, clusterReference):
    '''
    Saves docker compose file and runs it.
    '''
    cluster = None
    try:
        token = tokens.newCompositionToken(datastore)
        # retrieve cluster information from datastore
        cluster = datastore.getCluster(clusterReference)
        if cluster == None:
            raise errors.ControllerError("Cluster does not exist.")
        # Check docker
        endpoint = cluster['nodes'][0]['endpoint']
        dk = docker.dockerClient(endpoint, settings.DK_DEFAULT_MASTER_CLIENT_CERTS)

        dockercheck = docker.checkDocker(dk)
        if dockercheck is not True:
            raise errors.ControllerError("Error in cluster. Docker error: " + dockercheck)

        # Create composition in datastore
        datastorecomposition = {'token':token, 'cluster':clusterReference, 'status':'providing', 'description':'Providing data'}
        datastore.addComposition(token, datastorecomposition)

        # Save compose file
        try:
            files.saveComposeFile(token, composefile)
        except os.error:
            files.deleteComposeFile(token)
            datastore.delComposition(token)
            raise errors.OperationError("Couldn't create composition in the filesystem")

        # Launch composition
        docker.runComposition(datastore, token, dk=dk)

        return datastorecomposition
    except dataStore.DataStoreError, e:
        aux = errors.ControllerError("Runtime error: "+ e.message)
        return aux.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ str(e))
        return aux.getResponse()

def checkcompose(datastore, token, detail=False):
    '''
    Checks if containers up, checks if it is under deployment and in case it has finished, checks if it was succefully or not.
    '''
    try:
        # retrieve compose information in datastore
        compose = datastore.getComposition(token)
        if compose == None:
            raise errors.NotFoundError("Composer does not exist.")

        # Check previous stored status
        if compose['status']=='providing':
            if not docker.isComposeRunning(token):
                bErrors = docker.getComposeErrors(token)
                if bErrors == None: # finished and no errors
                    # update datastore
                    compose['status']='finished'
                    compose['description']='Deployment completes without errors.'
                    datastore.updateComposition(token, compose)
                else:               # finished but with errors
                    # update datastore
                    compose['status']='error'
                    compose['description']='Deployment finished unsuccefully.'
                    datastore.updateComposition(token, compose)
            else:
                pass
        elif compose['status']=='finished':
            pass
        else:
            pass

        if detail:
            pull_log = docker.getPullLog(token)
            up_log = docker.getUpLog(token)
            compose['pull_log'] = '' if pull_log==None else pull_log
            compose['up_log'] = '' if up_log==None else up_log

        return compose, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        raise e
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
