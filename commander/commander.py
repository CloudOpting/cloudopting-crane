from flask import Flask
from flask.ext.restplus import Api, apidoc, Resource, reqparse, fields


app = Flask(__name__)
api = Api(app)


@api.route('/build')
class BuildService(Resource):
    def get(self):
        return 'build:get'

    def post(self):
        return 'build:post'

@api.route('/build/<int:token>')
class BuildProcess(Resource):
    def get(self, token):
        return 'build/<token>:get'

    def delete(self, token):
        return 'build/<token>:delete'

@api.route('/cluster')
class ClusterService(Resource):
    def post(self):
        return 'cluster:post'

@api.route('/cluster/<int:token>')
class ClusterInstance(Resource):
    def get(self, token):
        return 'cluster/<token>:get'

    def delete(self, token):
        return 'cluster/<token>:delete'

@api.route('/composer')
class ComposerService(Resource):
    def post(self):
        return 'composer:post'

@api.route('/composer/<int:token>')
class ComposerDeployment(Resource):
    def get(self, token):
        return 'composer/<token>:get'

    def delete(self, token):
        return 'composer/<token>:delete'



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
