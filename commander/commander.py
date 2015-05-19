from flask import Flask
from flask.ext.restful import Api, Resource, reqparse, fields


app = Flask(__name__)
api = Api(app)

class About(Resource):
    def get(self):
        return 'An entry point to handle a Docker infrastructure.'


class BuildService(Resource):
    def get(self):
        return 'build:get'

    def post(self):
        return 'build:post'

class BuildProcess(Resource):
    def get(self, token):
        return 'build/<token>:get'

    def delete(self, token):
        return 'build/<token>:delete'

class ClusterService(Resource):
    def post(self):
        return 'cluster:post'

class ClusterInstance(Resource):
    def get(self, token):
        return 'cluster/<token>:get'

    def delete(self, token):
        return 'cluster/<token>:delete'


class ComposerService(Resource):
    def post(self):
        return 'composer:post'

class ComposerDeployment(Resource):
    def get(self, token):
        return 'composer/<token>:get'

    def delete(self, token):
        return 'composer/<token>:delete'


api.add_resource(About, '/about')
api.add_resource(BuildService, '/build')
api.add_resource(BuildProcess, '/build/<int:token>')
api.add_resource(ClusterService, '/cluster')
api.add_resource(ClusterInstance, '/cluster/<int:token>')
api.add_resource(ComposerService, '/composer')
api.add_resource(ComposerDeployment, '/composer/<int:token>')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
