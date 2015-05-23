from flask import Flask
from flask.ext.restplus import Api, apidoc, Resource, reqparse, fields, marshal_with
from schemas import builderSchemas, clusterSchemas, composerSchemas, contextSchemas

app = Flask(__name__)
api = Api(app, version='0.5', title='Docker commander API',
    description='An unified API to all Docker operations.',)

# Methods mapped in routes.

# Build API

builder_ns = api.namespace('builder', description='Building related operations')

@builder_ns.route('/contexts')
class ContextService(Resource):
    @api.doc(description='Retrieve list of contexts.')
    @marshal_with(contextSchemas.context_process_list_response)
    def get(self):
        # retrieve list
        result = {}
        result['numberOfContexts'] = 1
        result['listOfContexts'] = ['Th151s4t0k3n']
        return result

    @api.doc(description='Create new context.')
    @marshal_with(contextSchemas.context_basic_status_response)
    def post(self):
        # create new context and download modules
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'queued'
        result['description'] = 'Added to the queue. Waiting for a worker to start the process.'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

@builder_ns.route('/contexts/<token>')
@api.doc(params={'token': 'Token that identifies the context.'})
class Context(Resource):
    @api.doc(description='Get information about a context.')
    @marshal_with(contextSchemas.context_detailed_status_response)
    def get(self, token):
        # retrieve information
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'preparing'
        result['description'] = 'Downloading modules.'
        result['log'] = ""
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

    @api.doc(description='Remove a context and the related data.')
    @marshal_with(contextSchemas.context_basic_status_response)
    def delete(self, token):
        # retrieve information
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'stopping'
        result['description'] = 'Stopping the building and removing temporal data.'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result


@builder_ns.route('/images')
class BuildService(Resource):
    @api.doc(description='Retrieve list of processes.')
    @marshal_with(builderSchemas.build_process_list_response)
    def get(self):
        # retrieve list
        result = {}
        result['numberOfProcesses'] = 1
        result['listOfProcesses'] = ['Th151s4t0k3n']
        return result

    @api.doc(description='Start a build process.')
    @marshal_with(builderSchemas.build_basic_status_response)
    def post(self):
        # start the building
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'queued'
        result['description'] = 'Added to the queue. Waiting for a worker to start the process.'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

@builder_ns.route('/images/<token>')
@api.doc(params={'token': 'Token that identifies the building process.'})
class BuildProcess(Resource):
    @api.doc(description='Get information about a build process.')
    @marshal_with(builderSchemas.build_detailed_status_response)
    def get(self, token):
        # retrieve information
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'building'
        result['description'] = 'Image is under construction.'
        result['log'] = "Sending build context to Docker daemon 3.072 kB\nSending build context to Docker daemon \nStep 0 : FROM python:2-onbuild\n# Executing 3 build triggers\nTrigger 0, COPY requirements.txt /usr/src/app/\nStep 0 : COPY requirements.txt /usr/src/app/\nTrigger 1, RUN pip install -r requirements.txt\nStep 0 : RUN pip install -r requirements.txt\n ---> Running in 524e23eac476\nCollecting Flask==0.10.1 (from -r requirements.txt (line 1))\n  Downloading Flask-0.10.1.tar.gz (544kB)\nCollecting flask-restplus (from -r requirements.txt (line 2))\n  Downloading flask_restplus-0.7.1-py2.py3-none-any.whl (445kB)\nCollecting Werkzeug>=0.7 (from Flask==0.10.1->-r requirements.txt (line 1))\n  Downloading Werkzeug-0.10.4-py2.py3-none-any.whl (293kB)\nCollecting Jinja2>=2.4 (from Flask==0.10.1->-r requirements.txt (line 1))\n  Downloading Jinja2-2.7.3.tar.gz (378kB)\nCollecting itsdangerous>=0.21 (from Flask==0.10.1->-r requirements.txt (line 1))\n  Downloading itsdangerous-0.24.tar.gz (46kB)\nCollecting flask-restful>=0.3.2 (from flask-restplus->-r requirements.txt (line 2))\n  Downloading Flask_RESTful-0.3.2-py2.py3-none-any.whl\nCollecting markupsafe (from Jinja2>=2.4->Flask==0.10.1->-r requirements.txt (line 1))\n  Downloading MarkupSafe-0.23.tar.gz\nCollecting aniso8601>=0.82 (from flask-restful>=0.3.2->flask-restplus->-r requirements.txt (line 2)\nDownloading aniso8601-1.0.0.tar.gz (44kB)\nCollecting pytz (from flask-restful>=0.3.2->flask-restplus->-r requirements.txt (line 2))\n  Downloading pytz-2015.4-py2.py3-none-any.whl (475kB)\nCollecting six>=1.3.0 (from flask-restful>=0.3.2->flask-restplus->-r requirements.txt (line 2))\n  Downloading six-1.9.0-py2.py3-none-any.whl\n"
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

    @api.doc(description='Remove a building process and the related data.')
    @marshal_with(builderSchemas.build_basic_status_response)
    def delete(self, token):
        # retrieve information
        result = {}
        result['token'] = 'Th151s4t0k3n'
        result['status'] = 'stopping'
        result['description'] = 'Stopping the building and removing temporal data.'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result


# Cluster API

cluster_ns = api.namespace('cluster', description='Cluster related operations')

@cluster_ns.route('')
class ClusterService(Resource):
    @api.doc(description='Create a new swarm cluster.')
    @marshal_with(clusterSchemas.cluster_basic_status_response)
    def post(self):
        # start the process that creates the cluster
        result = {}
        result['token'] = 'An073rt0k3n'
        result['status'] = 'accepted'
        result['description'] = 'Request accepted. Format correct.'
        result['numberOfmachines'] = 1
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

@cluster_ns.route('/<token>')
@api.doc(params={'token': 'Token that identifies the docker swarm cluster.'})
class ClusterInstance(Resource):
    @api.doc(description='Get information about a docker swarm cluster.')
    @marshal_with(clusterSchemas.cluster_detailed_status_response)
    def get(self, token):
        # retrieve general info about the cluster
        result = {}
        result['token'] = 'An073rt0k3n'
        result['status'] = 'running'
        result['description'] = 'Master is up with all the nodes attached to it.'
        result['numberOfmachines'] = 1
        machine1 = {'reference': '192.168.7.9', 'status': 'running'}
        result['machines']=[]
        result['machines'].append(machine1)
        node1 = {'reference': '192.168.7.9', 'status': 'connected', 'resources': {'memAvailable':512, 'memUsed':124, 'cpuAvailable': 2, 'cpuUsed': 1}, 'runningContainers': 3}
        result['nodes']=[]
        result['nodes'].append(node1)
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

    @api.doc(description='Destroy a cluster and the related data.')
    @marshal_with(clusterSchemas.cluster_basic_status_response)
    def delete(self, token):
        # start the process that creates the cluster
        result = {}
        result['token'] = 'An073rt0k3n'
        result['status'] = 'stopping'
        result['description'] = 'Unlinking the nodes, stopping master.'
        result['numberOfmachines'] = 1
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result


# Composer API

composer_ns = api.namespace('composer', description='Composer related operations')

@composer_ns.route('')
class ComposerService(Resource):
    @api.doc(description='Instance a container based service by deploying and linking the containers defined in the docker-compose.yml.')
    @marshal_with(composerSchemas.composer_basic_status_response)
    def post(self):
        # start to deploy the composition
        result = {}
        result['token'] = 'Y35th151sAt0k3n'
        result['status'] = 'accepted'
        result['description'] = 'Information accepted. It will start to deploy soon.'
        result['clusterId'] = 'An073rt0k3n'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result

@composer_ns.route('/<token>')
@api.doc(params={'token': 'Token that identifies the docker composition'})
class ComposerDeployment(Resource):
    @api.doc(description='Get information about a docker container composition.')
    @marshal_with(composerSchemas.composer_detailed_status_response)
    def get(self, token):
        # start to deploy the composition
        result = {}
        result['token'] = 'Y35th151sAt0k3n'
        result['status'] = 'running'
        result['description'] = 'All the containers of the composition are up running.'
        result['clusterId'] = 'An073rt0k3n'
        container1 = {'reference': 'asia_apache_1', 'status': 'running', 'networkInformation':{'address':'172.82.64.9', 'exposed':'80:8080'}, 'volumes':['/usr/var/www', '/var/logs/httpd']}
        container2 = {'reference': 'asia_mysql_1', 'status': 'running', 'networkInformation':{'address':'172.82.64.8', 'exposed':''}, 'volumes':['/usr/var/www', '/var/logs/httpd']}
        container3 = {'reference': 'asia_solr_1', 'status': 'running', 'networkInformation':{'address':'172.82.64.7', 'exposed':''}, 'volumes':['/usr/var/mysqldata', '/var/logs/mysqld']}
        result['containers']=[]
        result['containers'].append(container1)
        result['containers'].append(container2)
        result['containers'].append(container3)
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result


    @api.doc(description='Destroy the container composition and the related data.')
    @marshal_with(composerSchemas.composer_detailed_status_response)
    def delete(self, token):
        # start to deploy the composition
        result = {}
        result['token'] = 'Y35th151sAt0k3n'
        result['status'] = 'stopping'
        result['description'] = 'Halting contianers and removing them.'
        result['clusterId'] = 'An073rt0k3n'
        #result['lastChecked'] = datetime.datetime.utcnow().isoformat()
        return result



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8888, debug=True)
