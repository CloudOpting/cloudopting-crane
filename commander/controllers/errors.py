class ControllerError(Exception):
    '''
    Generic error inside controller
    '''
    def __init__(self, message=None, errors=None, type='generic'):
        super(ControllerError, self).__init__(message)
        self.errors = errors
        self.message = message
        self.type = type

    def getResponse(self):
        return {'error': self.type, 'description': self.message}, 500

class OperationError(ControllerError):
    '''
    Error while doing any operation requested.
    '''
    def __init__(self, message=None, errors=None):
        super(OperationError, self).__init__(message, errors, 'operationError')

class NotFoundError(ControllerError):
    '''
    Resource not found
    '''
    def __init__(self, message=None, errors=None):
        super(NotFoundError, self).__init__(message, errors, 'notFound')
