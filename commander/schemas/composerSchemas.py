from flask.ext.restplus import fields


## TODO: create enum type for possible statuses.

## TODO: document this
composer_basic_status_response = {
    'token': fields.String,
    'status': fields.String,
    'description': fields.String,
    'clusterId': fields.String,
    'lastChecked': fields.DateTime(dt_format='iso8601')
}

container_description = {'reference': fields.String, 'status': fields.String, 'networkInformation': fields.String }

## TODO: document this
composer_detailed_status_response = composer_basic_status_response.copy()
composer_detailed_status_response['containers'] = fields.List(fields.Nested(container_description, allow_null = True))
