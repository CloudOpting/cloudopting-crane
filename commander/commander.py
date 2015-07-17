import os
import settings

from flask import Flask, request
from flask.ext.restplus import Api, apidoc, Resource, reqparse, fields, marshal_with
from schemas import builderSchemas, clusterSchemas, composerSchemas, generalSchemas
from werkzeug.datastructures import FileStorage

from controllers.builder import builderOps
from controllers.composer import composeOps
from controllers.management import managementOps
from datastore import dataStore
from datastore.dataStore import DataStore

app = Flask(__name__)
api = Api(app, version='0.5', title='Docker commander API',
    description='An unified API to all Docker operations.',)
datastore = DataStore(app)

# Common

errorResponseModel = api.model('Error', generalSchemas.basic_error_response)

def not_implemented():
    result = {'error':'not_implemented', 'description':'Feature not implemented yet'}
    return result, 500

def not_found():
    result = {'error':'not_found', 'description':'Resource not found'}
    return result, 404

# Extra routes

extra_ns = api.namespace('extra', description='Some extra functions.')

@extra_ns.route('/purge')
class Purge(Resource):

    @api.doc(description='Purge all data: contexts, compositions, files, etc. Note: if registry is deployed in the same docker engine, it will be also destroyed.')
    def get(self):
        return managementOps.purge(datastore)

@extra_ns.route('/tokens')
class Tokens(Resource):

    @api.doc(description='Get all tokens in datastore.')
    def get(self):
        return managementOps.getAllTokens(datastore)

@extra_ns.route('/alive')
class Alive(Resource):

    @api.doc(description='Dummy function. Returns a simple json with a message.')
    def get(self):
        return {'message':'I\'m alive'}


@extra_ns.route('/check')
class Check(Resource):

    @api.doc(description='Check several parameters in Crane status.')
    def get(self):
        from toolbox import docker
        dockerStatus = docker.checkDocker()
        return {'docker': 'correct' if dockerStatus==True else dockerStatus }

# Build API

builder_ns = api.namespace('builder', description='Building related operations')

## Response models
contextListModel = api.model('ContextList', builderSchemas.context_process_list_response)
contextInfoModel = api.model('ContextInfo', builderSchemas.context_basic_status_response)
contextDetailModel = api.model('ContextDetail', builderSchemas.context_detailed_status_response)
imageListModel = api.model('ImageList', builderSchemas.build_process_list_response)
imageInfoModel = api.model('ImageInfo', builderSchemas.build_basic_status_response)
imageDetailModel = api.model('ImageDetail', builderSchemas.build_detailed_status_response)

## Arguments models
contextArgs = api.parser()
contextArgs.add_argument('group', help='Group identifier. It will be added as a reference for images. The name of the images will be <groupId>/<imageName>.', location='form')
contextArgs.add_argument('puppetfile', type=FileStorage, help='Puppetfile that indicates the puppet modules needed in the context' , location='files')

buildArgs = api.parser()
buildArgs.add_argument('imageName', help='Desired image name.', location='form')
buildArgs.add_argument('contextReference', help='Reference (context token) to the context where the image will be build. If not set it will be build in a new and empty context.', location='form')
buildArgs.add_argument('dockerfile', type=FileStorage, help='Base image dockerfile' , location='files')
buildArgs.add_argument('puppetmanifest', type=FileStorage, help='Puppet manifest that contains the service definition for the image.' , location='files')

@builder_ns.route('/contexts')
class ContextService(Resource):

    @api.doc(description='Retrieve list of contexts.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(200, 'OK', contextListModel)
    def get(self):
        return builderOps.contextList(datastore)

    @api.doc(description='Create new context.', parser=contextArgs)
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(201, 'Created', contextInfoModel)
    def post(self):
        try:   # if group not provided it will use default group.
            return builderOps.newContext(puppetfile=request.files['puppetfile'], group=str(request.form['group']) ,datastore=datastore)
        except:
            return builderOps.newContext(puppetfile=request.files['puppetfile'], datastore=datastore)


@builder_ns.route('/contexts/<token>')
@api.doc(params={'token': 'Token that identifies the context.'})
class Context(Resource):

    @api.doc(description='Get information about a context.' )
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', contextDetailModel)
    def get(self, token):
        return builderOps.checkContext(datastore=datastore, token=token)

    @api.doc(description='Remove a context and the related data.' )
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', contextInfoModel)
    def delete(self, token):
        return builderOps.deleteContext(datastore, token)

@builder_ns.route('/contexts/<token>/detail')
@api.doc(params={'token': 'Token that identifies the context.'})
class ContextDetails(Resource):

    @api.doc(description='Get detailed information about a context.' )
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', contextDetailModel)
    def get(self, token):
        return builderOps.checkContext(datastore=datastore, token=token, detail=True)

@builder_ns.route('/images')
class BuildService(Resource):

    @api.doc(description='Retrieve list of processes.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(201, 'OK', imageListModel)
    def get(self):
        return not_implemented()

    @api.doc(description='Start a build process.', parser=buildArgs)
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(201, 'Created', imageInfoModel)
    def post(self):
        return builderOps.newImage(datastore=datastore, contextReference=str(request.form['contextReference']), imageName=str(request.form['imageName']), dockerfile=request.files['dockerfile'], puppetmanifest=request.files['puppetmanifest'])


@builder_ns.route('/images/<token>')
@api.doc(params={'token': 'Token that identifies the building process.'})
class BuildProcess(Resource):

    @api.doc(description='Get information about a build process.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', imageDetailModel)
    def get(self, token):
        return builderOps.checkImage(datastore, token)

    @api.doc(description='Remove a building process and the related data.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', imageInfoModel)
    def delete(self, token):
        return builderOps.deleteImage(datastore, token)

@builder_ns.route('/images/<token>/detail')
@api.doc(params={'token': 'Token that identifies the building process.'})
class BuildProcessDetail(Resource):

    @api.doc(description='Get detailed information about a build process.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', imageDetailModel)
    def get(self, token):
        return builderOps.checkImage(datastore, token, detail=True)

# Cluster API

cluster_ns = api.namespace('cluster', description='Cluster related operations')

## Response models
clusterInfoModel = api.model('ClusterInfo', clusterSchemas.cluster_basic_status_response)
clusterDetailModel = api.model('ClusterDetail', clusterSchemas.cluster_detailed_status_response)

## Arguments models
machineArgs = api.parser()
machineArgs.add_argument('hostname', help='Machine hostname or IP where is accesible.', location='form')
machineArgs.add_argument('port', type=int, help='SSH port.', location='form')
machineArgs.add_argument('privateKey', type=FileStorage, help='In case of privateKey-passphrase credentials: private key with access credentials.' , location='files')
machineArgs.add_argument('passphrase', help='In case of privateKey-passphrase credentials: passphrase to decode.', location='form')
machineArgs.add_argument('user', help='In case of user-password credentials: user.', location='form')
machineArgs.add_argument('password', help='In case of user-password credentials: password.', location='form')

@cluster_ns.route('')
class ClusterService(Resource):

    @api.doc(description='Create a new swarm cluster.', parser=machineArgs)
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(201, 'Created', clusterInfoModel)
    def post(self):
        return not_implemented()


@cluster_ns.route('/<token>')
@api.doc(params={'token': 'Token that identifies the docker swarm cluster.'})
class ClusterInstance(Resource):

    @api.doc(description='Add a new machine to a swarm cluster.', parser=machineArgs)
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'Created', clusterInfoModel)
    def put(self):
        return not_implemented()

    @api.doc(description='Get information about a docker swarm cluster.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', clusterDetailModel)
    def get(self, token):
        return not_implemented()

    @api.doc(description='Destroy a cluster and the related data.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', clusterInfoModel)
    def delete(self, token):
        return not_implemented()


# Composer API

composer_ns = api.namespace('composer', description='Composer related operations')

## Response models
composerInfoModel = api.model('ComposerInfo', composerSchemas.composer_basic_status_response)
composerDetailModel = api.model('ComposerDetail', composerSchemas.composer_detailed_status_response)

## Arguments models
composerArgs = api.parser()
composerArgs.add_argument('clusterToken', help='Reference to the cluster (token used in the \'cluster\' operations). If not provided, the deploy will be local.', location='form')
composerArgs.add_argument('composefile', type=FileStorage, help='Docker-compose.yml file that specifies how to compose the service.' , location='files')

@composer_ns.route('')
class ComposerService(Resource):

    @api.doc(description='Instance a container based service by deploying and linking the containers defined in the docker-compose.yml.', parser=composerArgs)
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(201, 'Created', composerInfoModel)
    def post(self):
        try:   # detect if clusterToken has been provided
            return composeOps.newComposition(datastore, composefile=request.files['composefile'], clusterReference=str(request.form['clusterToken']))
        except:
            return composeOps.newComposition(datastore, composefile=request.files['composefile'])

@composer_ns.route('/<token>')
@api.doc(params={'token': 'Token that identifies the docker composition'})
class ComposerDeployment(Resource):

    @api.doc(description='Get information about a docker container composition.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', composerDetailModel)
    def get(self, token):
        return not_implemented()

    @api.doc(description='Destroy the container composition and the related data.')
    @api.response(500, 'Error processing the request', errorResponseModel)
    @api.response(404, 'Not found', errorResponseModel)
    @api.response(200, 'OK', composerDetailModel)
    def delete(self, token):
        return not_implemented()

if __name__ == '__main__':
    app.run(host=settings.WS_BIND_IP, port=settings.WS_BIND_PORT, debug=(True if os.environ.get('DEBUG')=='true' else False))
