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
        aux = puppetUtils.checkPuppetfile(token)
        if not aux==True:
            fileUtils.deleteDir(token)
            raise errors.OperationError("Syntax error in provided puppetfile: " + aux)

        # Launch build operation
        puppetUtils.buildContext(token)

        # Create context in datastore
        datastorecontext = {'token':token, 'status':'building', 'description':'Under creation'}
        datastore.addContext(token, datastorecontext)

        return datastorecontext

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()



def checkContext(datastore, token):
    try:
        # retrieve context information in datastore
        context = datastore.getContext(token)
        if context == None:
            raise errors.NotFoundError("Token does not exist.")

        # Check previous stored status
        if context['status']=='building':
            if not puppetUtils.isBuildingContextRunning(token):
                bErrors = puppetUtils.getBuildingErrors(token)
                if bErrors == None: # finished and no errors
                    # update datastore
                    context['status']='finished'
                    context['description']='Build finished without errors'
                    datastore.updateContext(token, context)
                    # add log to response
                    context['log'] = puppetUtils.getBuildingLog(token)
                else:               # finished but with errors
                    # update datastore
                    context['status']='error'
                    context['description']='Build finished unsuccefully.'
                    datastore.updateContext(token, context)
                    # add log to response
                    context['log'] = puppetUtils.getBuildingErrors(token)
            else:
                # add log to response
                context['log'] = puppetUtils.getBuildingLog(token)

        elif context['status']=='finished':
            # add log to response
            context['log'] = puppetUtils.getBuildingLog(token)
        else:
            # add log to response
            context['log'] = puppetUtils.getBuildingErrors(token)

        return context

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        raise e
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def deleteContext(datastore, token):
    try:
        # retrieve context information in datastore
        context = datastore.getContext(token)
        if context == None:
            raise errors.NotFoundError("Token does not exist.")

        # stop process if running
        puppetUtils.stopBuildingContext(token)
        # delete folder
        fileUtils.deleteDir(token)
        # delete from datastore
        datastore.delContext(token)
        # fake context just to return a response
        context = {}
        context['status']='deleted'
        context['description']='Context has been removed and will not be accesible anymore.'
        return context
    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
