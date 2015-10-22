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
