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
    'tag' : fields.String
}


## TODO: document this
build_detailed_status_response = build_basic_status_response.copy()
build_detailed_status_response['log'] = fields.String

## TODO: create enum type for possible statuses (context).

## TODO: document this
context_process_list_response = {
    'contexts': fields.List(fields.String)
}

## TODO: document this
context_basic_status_response = {
    'token': fields.String,
    'group': fields.String,
    'status': fields.String,
    'description': fields.String
}


## TODO: document this
context_detailed_status_response = context_basic_status_response.copy()
context_detailed_status_response['log'] = fields.String
