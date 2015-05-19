from flask import Flask
from flask.ext.restplus import Api, apidoc, Resource, reqparse, fields


app = Flask(__name__)
api = Api(app, version='0.5', title='Docker commander API',
    description='An unified API to all Docker operations.',)


@api.route('/build')
class BuildService(Resource):
    @api.doc(description='Retrieve list of processes.')
    def get(self):
        return 'build:get'

    @api.doc(description='Start a build process.')
    def post(self):
        return 'build:post'

@api.route('/build/<int:token>')
@api.doc(params={'token': 'Token that identifies the building process.'})
class BuildProcess(Resource):
    @api.doc(description='Get information about a build process.')
    def get(self, token):
        return 'build/<token>:get'

    @api.doc(description='Remove a building process and the related data.')
    def delete(self, token):
        return 'build/<token>:delete'

@api.route('/cluster')
class ClusterService(Resource):
    @api.doc(description='Create a new swarm cluster.')
    def post(self):
        return 'cluster:post'

@api.route('/cluster/<int:token>')
@api.doc(params={'token': 'Token that identifies the docker swarm cluster.'})
class ClusterInstance(Resource):
    @api.doc(description='Get information about a docker swarm cluster.')
    def get(self, token):
        return 'cluster/<token>:get'

    @api.doc(description='Destroy a cluster and the related data.')
    def delete(self, token):
        return 'cluster/<token>:delete'

@api.route('/composer')
class ComposerService(Resource):
    @api.doc(description='Instance a container based service by deploying and linking the containers defined in the docker-compose.yml.')
    def post(self):
        return 'composer:post'

@api.route('/composer/<int:token>')
@api.doc(params={'token': 'Token that identifies the docker composition'})
class ComposerDeployment(Resource):
    @api.doc(description='Get information about a docker container composition.')
    def get(self, token):
        return 'composer/<token>:get'

    @api.doc(description='Destroy the container composition and the related data.')
    def delete(self, token):
        return 'composer/<token>:delete'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
