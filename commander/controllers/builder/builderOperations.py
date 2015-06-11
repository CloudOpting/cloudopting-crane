import settings
import os

from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from controllers import errors
import puppetUtils
import dockerUtils
import fileUtils

def newContext(puppetfile, datastore, contextName=''):
    '''
    Reads and checks puppetfile, creates the directory in the filesystem and launch puppetfile processing.
    '''
    try:
        token = tokens.newContextToken(datastore)

        # Create context in filesystem
        try:
            fileUtils.createContextDir(token)
        except os.error:
            fileUtils.deleteContextDir(token)
            raise errors.OperationError("Couldn't create context in the filesystem")

        # Save puppetfile
        fileUtils.savePuppetfile(token, puppetfile)

        # Check puppetfile
        aux = puppetUtils.checkPuppetfile(token)
        if not aux==True:
            fileUtils.deleteContextDir(token)
            raise errors.OperationError("Syntax error in provided puppetfile: " + aux)

        # Launch build operation
        puppetUtils.buildContext(token)

        # Create context in datastore
        datastorecontext = {'token':token, 'contextName':contextName, 'status':'building', 'description':'Under creation', 'images':[]}
        datastore.addContext(token, datastorecontext)

        return datastorecontext

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()



def checkContext(datastore, token):
    '''
    Checks if the context exists, checks if it is under construction and in case it has finished, checks if it was succefully or not.
    '''
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

        return context, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        raise e
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def deleteContext(datastore, token):
    '''
    Stops the building process of a context (if running) and deletes the folder in the filesystem and the entry in the datastore.
    '''
    try:
        # retrieve context information in datastore
        context = datastore.getContext(token)
        if context == None:
            raise errors.NotFoundError("Token does not exist.")

        # stop process if running
        puppetUtils.stopBuildingContext(token)
        # delete folder
        fileUtils.deleteContextDir(token)
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


def newImage(datastore, contextReference, imageName, dockerfile, puppetmanifest):
    '''
    Saves the files in the filesystem, and launch the build process
    '''
    try:
        token = tokens.newImageToken(datastore, contextReference, imageName)

        # Check if context exists and if it is completed
        contextInfo, statusCode = checkContext(datastore, contextReference)
        if statusCode == 404:
            raise errors.OperationError("Context does not exist")
        if not statusCode == 200:
            raise errors.OperationError("Error while inspecting context")
        if not contextInfo['status']=='finished':
            raise errors.OperationError("Context is not ready")

        # Create image in datastore
        datastoreimage = {'token':token, 'context':contextReference, 'imageName':imageName, 'status':'building', 'description':'Under creation'}
        datastore.addImage(contextReference, token, datastoreimage)

        # Create image in filesystem and save Dockerfile and Puppetmanifest
        try:
            fileUtils.createImageDir(contextReference, imageName)
            fileUtils.saveDockerfile(contextReference, imageName, dockerfile)
            fileUtils.savePuppetManifest(contextReference, imageName, puppetmanifest)
        except os.error:
            fileUtils.delImage(contextReference, imageName)
            datastore.delImage(token)
            raise errors.OperationError("Couldn't create image in the filesystem")

        # Launch build operation
        dockerUtils.buildImage(datastore, contextReference, imageName, token)

        return datastoreimage
    except dataStore.DataStoreError, e:
        aux = errors.ControllerError("Runtime error: "+ e.message)
        return aux.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def checkImage(datastore, imageToken):
    '''
    Checks if the image exists, checks if it is under construction and in case it has finished, checks if it was succefully or not.
    '''
    try:
        # get context
        image = datastore.getImage(imageToken)
        if image == None:
            raise errors.NotFoundError("Image does not exist.")
        # Check previous stored status
        if image['status']=='building':
            if not dockerUtils.isDockerBuildRunning(image['context'], image['imageName']):
                bErrors = dockerUtils.getBuildErrors(image['context'], image['imageName'])
                if bErrors == None: # finished and no errors
                    # update datastore
                    image['status']='finished'
                    image['description']='Build finished without errors'
                    datastore.updateImage(imageToken, image)
                    # add log to response
                    image['log'] = dockerUtils.getBuildLog(image['context'], image['imageName'])
                else:               # finished but with errors
                    # update datastore
                    image['status']='error'
                    image['description']='Build finished unsuccefully.'
                    datastore.updateImage(imageToken, image)
                    # add log to response
                    image['log'] = dockerUtils.getBuildErrors(image['context'], image['imageName'])
            else:
                # add log to response
                image['log'] = dockerUtils.getBuildLog(image['context'], image['imageName'])
        elif image['status']=='finished':
            # add log to response
            image['log'] = dockerUtils.getBuildLog(image['context'], image['imageName'])
        else:
            # add log to response
            image['log'] = dockerUtils.getBuildErrors(image['context'], image['imageName'])

        return image, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
