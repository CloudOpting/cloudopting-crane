import settings
import os

from controllers import errors
from toolbox import files
from toolbox import docker
from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore

def __obtainDockerHostInfo__(endpoint, apiVersion):
    # Obtain information about docker daemon listening on endpoint
    info = None

    try:
        if apiVersion:
            info = docker.dockerInfo(dockerClient=endpoint, version=apiVersion)
        else:
            info = docker.dockerInfo(dockerClient=endpoint)
    except Exception, e:
        raise errors.ControllerError("Error while connecting with provided docker host.")

    if not info:
        raise errors.ControllerError("Could not validate docker daemon on provided endpoint.")

    return info

def newSingleProvisionedMachineCluster(datastore, endpoint, apiVersion=None):
    '''
    Set a preprovisioned single-machine cluster. 'endpoint' is the Docker host api endpoint.
    '''
    try:
        info = __obtainDockerHostInfo__(endpoint, apiVersion)

        # Generate token
        token = tokens.newClusterToken(datastore)

        # Add to filesystem: for this simple already provisioned machine, only the folder will be created
        try:
            files.createClusterDir(token)
        except os.error:
            files.deleteClusterDir(token)
            raise errors.OperationError("Couldn't create cluster reference in the filesystem")

        # Add to datastore
        datastorecluster = {'token':token, 'status':'ready', 'description':'Ready to use', 'numberOfMachines':1, 'type':'simple-preprovisioned', 'endpoint':endpoint}
        datastore.addCluster(token, datastorecluster)

        return datastorecluster, 200

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def checkCluster(datastore, token, detail=False):
    '''
    Retrieve information from the cluster.
    '''
    try:
        status = 200
        # Retrieve cluster information in datastore
        cluster = datastore.getCluster(token)
        if cluster == None:
            raise errors.NotFoundError("Cluster does not exist.")

        # Ask docker daemon about himself
        info = None
        try:
            info = __obtainDockerHostInfo__(endpoint, apiVersion)
        except Exception, e:
            cluster['status']='error'
            cluster['description']='Cannot connect with docker daemon. Maybe it is down.'

        # update datastore
        datastore.updateCluster(token)

        # details
        if detail:
            cluster['detail']=info

        return cluster, 200

    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        raise e
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()

def deleteCluster(datastore, token):
    '''
    Deletes the cluster and all reference with it.
    '''
    try:
        # Retrieve cluster information in datastore
        cluster = datastore.getCluster(token)
        if cluster == None:
            raise errors.NotFoundError("Cluster does not exist.")

        # stop cluster (depends on the type of cluster)
        if cluster['type'] is 'simple-preprovisioned':
            pass
        else:
            raise errors.ControllerError("Don't know how to remove a cluster of this type ("+ cluster['type'] + ")." )

        # delete folder
        files.deleteClusterDir(token)
        # delete from datastore
        datastore.delCluster(token)
        # fake cluster just to return a response
        cluster = {}
        cluster['status']='deleted'
        cluster['description']='Cluster has been removed and will not be accesible anymore.'
        return cluster
    except errors.NotFoundError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()
