from flask.ext.restplus import fields


## TODO: document this
basic_error_response = {
    'status': fields.String,
    'description': fields.String
}
