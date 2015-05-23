from flask.ext.restplus import fields

## TODO: create enum type for possible statuses.

## TODO: document this
build_process_list_response = {
    'numberOfProcesses': fields.Integer(default=0),
    'listOfProcesses': fields.List(fields.String)
}

## TODO: document this
build_basic_status_response = {
    'token': fields.String,
    'status': fields.String,
    'context': fields.String,
    'description': fields.String,
    'imageName' : fields.String,
    'lastChecked': fields.DateTime(dt_format='iso8601')
}


## TODO: document this
build_detailed_status_response = build_basic_status_response.copy()
build_detailed_status_response['log'] = fields.String
