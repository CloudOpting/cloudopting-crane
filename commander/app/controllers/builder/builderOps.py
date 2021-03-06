import settings
import os

from controllers import errors
from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore
from toolbox import puppet
from toolbox import docker
from toolbox import files
from threading import Thread

def contextList(datastore):
    '''
    Returns a list of contexts.
    '''
    try:
        listOfContexts = datastore.getContexts()
        return { 'contexts': [] if listOfContexts == None else listOfContexts }

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def newContext(datastore, puppetfile= None, group='default'):
    '''
    Reads and checks puppetfile, creates the directory in the filesystem and launch puppetfile processing.
    '''
    try:
        token = tokens.newContextToken(datastore)

        # Create context in filesystem
        try:
            files.createContextDir(token)
        except os.error:
            files.deleteContextDir(token)
            raise errors.OperationError("Couldn't create context in the filesystem")

        if not puppetfile == None:
            # Save puppetfile
            files.savePuppetfile(token, puppetfile)

            # Check puppetfile
            aux = puppet.checkPuppetfile(token)
            if not aux==True:
                files.deleteContextDir(token)
                raise errors.OperationError("Syntax error in provided puppetfile: " + aux)

            # Launch build operation
            puppet.buildContext(token)

            # Create context in datastore
            datastorecontext = {'token':token, 'group':group, 'status':'building', 'description':'Under creation', 'images':[]}
            datastore.addContext(token, datastorecontext)
        else:
            pid = os.path.join(settings.FS_BUILDS, token)
            pid = os.path.join(pid, settings.FS_DEF_CONTEXT_PID)
            files.createFile(pid,'')

            contextlog =  os.path.join(settings.FS_BUILDS, token)
            contextlog =  os.path.join(contextlog, settings.FS_DEF_CONTEXT_LOG)
            files.createFile(contextlog,'')

            contextlogE =  os.path.join(settings.FS_BUILDS, token)
            contextlogE =  os.path.join(contextlogE, settings.FS_DEF_CONTEXT_ERR_LOG)
            files.createFile(contextlogE,'')

            datastorecontext = {'token':token, 'group':group, 'status':'finished', 'description':'Build finished without errors', 'images':[]}
            datastore.addContext(token, datastorecontext)
            
        return datastorecontext

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()



def checkContext(datastore, token, detail=False):
    '''
    Checks if the context exists, checks if it is under construction and in case it has finished, checks if it was succefully or not.
    '''
    try:
        # retrieve context information in datastore
        context = datastore.getContext(token)
        if context == None:
            raise errors.NotFoundError("Context does not exist.")

        # Check previous stored status
        if context['status']=='building':
            if not puppet.isBuildingContextRunning(token):
                bErrors = puppet.getBuildingErrors(token)
                if bErrors == None: # finished and no errors
                    # update datastore
                    context['status']='finished'
                    context['description']='Build finished without errors'
                    datastore.updateContext(token, context)
                else:               # finished but with errors
                    # update datastore
                    context['status']='error'
                    context['description']='Build finished unsuccefully.'
                    datastore.updateContext(token, context)
            else:
                pass
        elif context['status']=='finished':
            pass
        else:
            pass

        if detail:
            log = puppet.getBuildingLog(token)
            # errLog = puppet.getBuildingErrors(token)
            context['log'] = '' if log==None else log
            # context['error_log'] = '' if errLog==None else errLog

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
        puppet.stopBuildingContext(token)
        # delete folder
        files.deleteContextDir(token)
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

def newBase(datastore, name, dockerfile):
    '''
    Build a new base image.
    '''
    try:
        # Create base in filesystem
        try:
            files.createBaseDir(name)
        except os.error:
            raise errors.OperationError("Couldn't create base in the filesystem. It may already exists.")

        # Save Dockerfile
        files.saveBaseDockerfile(name, dockerfile)

        # Launch build operation
        docker.buildBase(datastore, name)

        # Create base in datastore
        datastorebase = {'name':name, 'status':'building', 'description':'Under creation'}
        datastore.addBase(name, datastorebase)

        return datastorebase

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()



def listBases(datastore):
    '''
    List the available base images
    '''
    try:
        listOfBases = datastore.getBases()
        return { 'bases': [] if listOfBases == None else listOfBases }

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def checkBase(datastore, name, detail=False):
    '''
    Check the status of a base image
    '''
    try:
        # get base
        base = datastore.getBase(name)
        if base == None:
            raise errors.NotFoundError("Base does not exist.")

        # Check previous stored status
        if base['status']=='building':
            if not docker.isBaseBuildRunning(name):
                bErrors = docker.getBaseBuildErrors(name)
                if bErrors == None: # finished and no errors
                    # update datastore
                    base['status']='finished'
                    base['description']='Build finished without errors'
                    datastore.updateBase(name, base)
                else:               # finished but with errors
                    # update datastore
                    base['status']='error'
                    base['description']='Build finished unsuccefully.'
                    datastore.updateBase(name, base)
            else:
                pass
        elif base['status']=='finished':
            pass
        else:
            pass

        if detail:
            log = docker.getBaseBuildLog(name)
            errLog = docker.getBaseBuildErrors(name)
            base['log'] = '' if log==None else log
            base['error_log'] = '' if errLog==None else errLog

        return base, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def deleteBase(datastore, name):
    '''
    Delete a base image
    '''
    try:
        # get base
        base = datastore.getBase(name)
        if base == None:
            raise errors.NotFoundError("Base does not exist.")

        # check if building and stop in case
        docker.stopBaseBuild(name)

        # delete docker image
        if docker.deleteBaseImage(datastore, name) == False:
            raise errors.ControllerError("Can't delete docker base image.")

        # remove from filesystem
        files.deleteBaseDir(name)

        # remove from datastore
        datastore.delBase(name)

        base['status'] = 'deleted'
        base['description'] = ''

        return base, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def newImage(datastore, contextReference, imageName, puppetmanifest=None, base=None, dockerfile=None):
    '''
    Saves the files in the filesystem, and launch the build process
    '''
    try:
 #       imageName=''.join(ch for ch in imageName if ch.isalnum())
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
        datastoreimage = {'token':token, 'context':contextReference, 'imageName':imageName, 'status':'building', 'description':'Under creation', 'tag':datastore.getContext(contextReference)['group']+'/'+imageName.lower()}
        datastore.addImage(contextReference, token, datastoreimage)

        # Create image in filesystem and save Dockerfile and Puppetmanifest
        try:
            files.createImageDir(contextReference, imageName)
            if puppetmanifest!=None:
                filename= puppetmanifest.filename
                files.savePuppetManifest(contextReference, imageName, puppetmanifest, filename=filename)
            if dockerfile!=None:
                files.saveDockerfile(contextReference, imageName, dockerfile)
            if base!=None:
                baseImageName=settings.DK_DEFAULT_BASE_PROVIDER+'/'+base
                if docker.imageInRegistry(baseImageName) == False:
                    raise errors.OperationError("Base image '"+baseImageName+"' does not exist in private registry")
                files.createBaseDockerfile(contextReference, imageName, settings.DK_RG_ENDPOINT+'/'+baseImageName, filename)

        except os.error:
            files.deleteImageDir(contextReference, imageName)
            datastore.delImage(token)
            raise errors.OperationError("Couldn't create image in the filesystem")

        # Launch build operation
        docker.buildImage(datastore, contextReference, imageName, token)

        return datastoreimage
    except dataStore.DataStoreError, e:
        aux = errors.ControllerError("Runtime error: "+ e.message)
        return aux.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def checkImage(datastore, imageToken, detail=False):
    '''
    Checks if the image exists, checks if it is under construction and in case it has finished, checks if it was succefully or not.
    '''
    try:
        # get image
        image = datastore.getImage(imageToken)
        if image == None:
            raise errors.NotFoundError("Image does not exist.")

        # Check previous stored status
        if image['status']=='building':
            if not docker.isDockerBuildRunning(image['context'], image['imageName']):
                bErrors = docker.getBuildErrors(image['context'], image['imageName'])
                if bErrors == None: # finished and no errors
                    # update datastore
                    image['status']='finished'
                    image['description']='Build finished without errors'
                    datastore.updateImage(imageToken, image)
                else:               # finished but with errors
                    # update datastore
                    image['status']='error'
                    image['description']='Build finished unsuccefully.'
                    datastore.updateImage(imageToken, image)
            else:
                pass
        elif image['status']=='finished':
            pass
        else:
            pass

        if detail:
            log = docker.getBuildLog(image['context'], image['imageName'])
            errLog = docker.getBuildErrors(image['context'], image['imageName'])
            image['log'] = '' if log==None else log
            image['error_log'] = '' if errLog==None else errLog

        return image, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def deleteImage(datastore, imageToken):
    '''
    Deletes image and stops the build process.
    '''
    try:
        # get image
        image = datastore.getImage(imageToken)
        if image == None:
            raise errors.NotFoundError("Image does not exist.")

        # check if building and stop in case
        docker.stopBuild(image['context'], image['imageName'])

        # delete docker image
        if docker.deleteImage(datastore, imageToken) == False:
            raise errors.ControllerError("Can't delete docker image.")

        # remove from filesystem
        files.deleteImageDir(image['context'], image['imageName'])

        # remove from datastore
        datastore.delImage(imageToken)

        image['status'] = 'deleted'
        image['description'] = ''

        return image, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def aioBuild(datastore, puppetfile, imageName, dockerfile, puppetmanifest, group='default', synchronous=False):
    import time
    def __aioThread__(datastore, contextToken, imageName, dockerfile, puppetmanifest):
        # check context
        context = None
        while True:
            time.sleep(5)
            context = checkContext(datastore=datastore, token=contextToken)[0]

            if context['status'] is not 'building':
                break

        if context['status'] is not 'finished': # error case
            return

        # build image
        image = newImage(datastore=datastore,
                 contextReference=contextToken,
                 imageName=imageName,
                 dockerfile=dockerfile,
                 puppetmanifest=puppetmanifest
                )
        print image
        # check image
        while True:
            time.sleep(5)
            response = checkImage(datastore=datastore, imageToken=image['token'])
            image = response[0]
            if image['status'] is not 'building':
                break

        return context

    context = newContext(puppetfile=puppetfile, datastore=datastore, group=group)

    if context['status'] is 'building':
        if synchronous:
            return __aioThread__(datastore,
                          context['token'],
                          imageName,
                          dockerfile,
                          puppetmanifest
                         )
        else: # asynchronous
            thread = Thread(target = __aioThread__,
                            args=[datastore,
                                  context['token'],
                                  imageName,
                                  dockerfile,
                                  puppetmanifest
                                 ]
                           )
            thread.start()
    return context
