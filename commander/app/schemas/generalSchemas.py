from flask.ext.restplus import fields


## TODO: document this
basic_error_response = {
    'error': fields.String,
    'description': fields.String
}
