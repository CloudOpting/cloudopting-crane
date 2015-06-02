import settings
import os

from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from controllers import errors
import puppetUtils
import fileUtils

def newContext(puppetfile, datastore, contextName=None):
    '''
    Reads and checks puppetfile, creates directory and launch puppetfile processing.
    '''
    try:
        token = tokens.newCompositionToken()

        # Create context in filesystem
        try:
            fileUtils.createDir(token)
        except os.error:
            fileUtils.deleteDir(token)
            raise errors.OperationError("Couldn't create context in the filesystem")

        # Save puppetfile
        fileUtils.savePuppetfile(token, puppetfile)

        # Check puppetfile
        if puppetUtils.checkPuppetfile(token)==False:
            fileUtils.deleteDir(token)
            raise errors.OperationError("Syntax error in provided puppetfile")

        # Launch build operation
        if puppetUtils.buildContext(token)==False:
            fileUtils.deleteDir(token)
            raise errors.OperationError("Couldn't start process")

        # Create context in datastore
        datastorecontext = {'token':token, 'status':'waiting', 'description':'Under creation'}
        datastore.addContext(token, datastorecontext)

        return datastorecontext

    except Exception, e:
        raise errors.ControllerError("Unknown error: "+ e.message)
    except errors.ControllerError, e:
        return e.getResponse()



def checkContext(datastore, token):
    return datastore.getContext(token)
