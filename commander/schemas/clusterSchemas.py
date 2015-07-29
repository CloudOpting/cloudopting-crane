from flask.ext.restplus import fields


## TODO: create enum type for possible statuses.

## TODO: document this
cluster_basic_status_response = {
    'token': fields.String,
    'status': fields.String,
    'description': fields.String,
    'numberOfMachines': fields.Integer,
    'type': fields.String,
    'endpoint': fields.String,
    'detail': fields.String
}

machine_description = {'reference': fields.String, 'status': fields.String }
node_description = {'reference': fields.String, 'status': fields.String, 'resources': fields.String, 'runningContainers': fields.Integer }

## TODO: document this
cluster_detailed_status_response = cluster_basic_status_response.copy()
#cluster_detailed_status_response['machines'] = fields.List(fields.Nested(machine_description, allow_null = True))
#cluster_detailed_status_response['nodes'] = fields.List(fields.Nested(node_description, allow_null = True))
