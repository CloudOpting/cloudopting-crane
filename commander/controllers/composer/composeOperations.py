import settings
import os

from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from controllers import errors
from toolbox import docker
from toolbox import files

from builderOperations import checkContext

def newComposition(datastore, composefile, clusterReference=''):
    '''
    Saves docker compose file and runs it.
    '''
    try:
        token = tokens.newCompositionToken(datastore)

        # Pull images
        ## TODO: at the moment images are local, so it is not needed.

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
        if(clusterReference==''):
            docker.runComposition(datastore, token)
        else:
            ## TODO: at the momment images are local, but in the future you will can deploy compositions on remote docker hosts..
            ## Call here the runComposition method with the dockerClient parameter.
            raise ControllerError("Remote docker hosts feature not supported yet.")

        return datastorecomposition
    except dataStore.DataStoreError, e:
        aux = errors.ControllerError("Runtime error: "+ e.message)
        return aux.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ str(e))
        return aux.getResponse()
