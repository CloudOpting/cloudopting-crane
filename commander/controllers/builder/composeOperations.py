import settings
import os

from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from controllers import errors
import puppetUtils
import dockerUtils
import fileUtils

from builderOperations import checkContext

def newComposition(datastore, composefile, contextReference):
    '''
    Saves docker compose file in the context and runs it.
    '''
    try:
        token = tokens.newCompositionToken(datastore)

        # Check if context exists and if it is completed
        contextInfo, statusCode = checkContext(datastore, contextReference)
        if statusCode == 404:
            raise errors.OperationError("Context does not exist")
        if not statusCode == 200:
            raise errors.OperationError("Error while inspecting context")
        if not contextInfo['status']=='finished':
            raise errors.OperationError("Context is not ready")

        # Create composition in datastore
        datastorecomposition = {'token':token, 'context':contextReference, 'status':'providing', 'description':'Providing data'}
        datastore.addComposition(token, datastorecomposition)

        # Save compose file
        try:
            fileUtils.saveComposeFile(contextReference, composefile)
        except os.error:
            fileUtils.deleteComposeFile(contextReference)
            datastore.delComposition(token)
            raise errors.OperationError("Couldn't create composition in the filesystem")

        # Launch composition
        dockerUtils.runComposition(datastore, contextReference)

        return datastorecomposition
    except dataStore.DataStoreError, e:
        aux = errors.ControllerError("Runtime error: "+ e.message)
        return aux.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
