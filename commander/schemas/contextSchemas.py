from flask.ext.restplus import fields

## TODO: create enum type for possible statuses.

## TODO: document this
context_process_list_response = {
    'numberOfContexts': fields.Integer(default=0),
    'listOfContexts': fields.List(fields.String)
}

## TODO: document this
context_basic_status_response = {
    'token': fields.String,
    'status': fields.String,
    'description': fields.String,
    'lastChecked': fields.DateTime(dt_format='iso8601')
}


## TODO: document this
context_detailed_status_response = context_basic_status_response.copy()
context_detailed_status_response['log'] = fields.String
