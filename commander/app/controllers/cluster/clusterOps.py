import settings
import os

from controllers import errors
from toolbox import files
from toolbox import docker
from datastore import tokens
from datastore import dataStore
from datastore.dataStore import DataStore

def __obtainDockerHostInfo__(endpoint):
    # Obtain information about docker daemon listening on endpoint
    info = None

    try:
        dk = docker.dockerClient(base_url=endpoint, cert_path=settings.DK_DEFAULT_MASTER_CLIENT_CERTS)
        info = docker.dockerInfo(dk)
    except Exception, e:
        raise errors.ControllerError("Error while connecting with provided docker host. Endpoint: '"+str(endpoint)+"' exception:"+str(e))

    if not info:
        raise errors.ControllerError("Could not validate docker daemon on provided endpoint.")

    return info

def newSingleProvisionedMachineCluster(datastore, endpoint, apiVersion=None):
    '''
    Set a preprovisioned single-machine cluster. 'endpoint' is the Docker host api endpoint.
    '''
    try:
        info = __obtainDockerHostInfo__(endpoint)

        # Generate token
        token = tokens.newClusterToken(datastore)

        # Add to filesystem: for this simple already provisioned machine, only the folder will be created
        try:
            files.createClusterDir(token)
        except os.error:
            files.deleteClusterDir(token)
            raise errors.OperationError("Couldn't create cluster reference in the filesystem")

        # Add to datastore
        datastorecluster = {'token':token, 'status':'joining',
        'description':'Ready to use', 'numberOfNodes':1, 'type':'simple-preprovisioned',
        'nodes':[{'endpoint':endpoint, 'status':'joining'}]}
        datastore.addCluster(token, datastorecluster)

        return datastorecluster, 200

    except errors.ControllerError, e:
        return e.getResponse()
    except Exception, e:
        aux = errors.ControllerError("Unknown error: "+ e.message)
        return aux.getResponse()


def newProvisionedMachineCluster(datastore, endpoint, apiVersion=None):
    '''
    Set a preprovisioned single-machine cluster. 'endpoint' is the Docker host api endpoint.
    '''
    try:
        info = __obtainDockerHostInfo__(endpoint)
        dk = docker.dockerClient(base_url=endpoint, cert_path=settings.DK_DEFAULT_MASTER_CLIENT_CERTS)

        # Generate token
        token = tokens.newClusterToken(datastore)

        # Add to filesystem: for this simple already provisioned machine, only the folder will be created
        try:
            files.createClusterDir(token)
        except os.error:
            files.deleteClusterDir(token)
            raise errors.OperationError("Couldn't create cluster reference in the filesystem")

        # Add to datastore
        datastorecluster = {'token':token, 'status':'joining',
        'description':'Ready to use', 'numberOfNodes':1, 'type':'swarm',
        'nodes':[{'endpoint':endpoint, 'status':'joining'}]}
        datastore.addCluster(token, datastorecluster)

        docker.createOneNodeSwarm(datastore, token, dk)

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

        # Ask docker daemons
        clusterStatus = 'ready'
        for node in cluster['nodes']:
            info = None
            try:
                info = __obtainDockerHostInfo__(node['endpoint'])
                if info['Driver'] is not None:
                    node['status']='ready'
                else:
                    node['status']='error'
                    clusterStatus = 'error'
                    cluster['description']='Unexpected response from node \''+node['endpoint']+'\'.'
            except Exception, e:
                node['status']='error'
                clusterStatus='error'
                cluster['description']='Cannot connect with node \''+node['endpoint']+'\'. Maybe it is down.'

        # update datastore
        datastore.updateCluster(token, cluster)

        # details
        if detail:
            cluster['detail']=info

        cluster['status'] = clusterStatus

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
