from flask.ext.cache import Cache

class DataStoreError(Exception):
    pass

class DataStore:
    def __init__(self, app):
        self.app = app
        self.cache = Cache(app, config{'CACHE_TYPE':'simple'})

    # generic methods

    def set(self, key, value):
        '''
        Sets value to a key
        '''
        pass

    def add(self, key, value):
        '''
        Adds a item to a list
        '''
        pass

    def get(self, key):
        '''
        Gets a value from it key
        '''
        pass

    def delete(self, key):
        '''
        Deletes a key-value pair
        '''
        pass


    def delete(self, listKey, elementKey):
        '''
        Deletes a element in a list
        '''
        pass

    def checkIfExists(self, key):
        '''
        Checks if a key is defined
        '''
        pass

    def checkIfExists(self, listKey, elementKey):
        '''
        Checks if a element exists in a list
        '''
        pass

    def raiseIfDifferent(self, a, b):
        if a != b:
            raise DataStoreError('Error: \'' + a + '\' and \'' + b + '\' are different.')

    def raiseIfNotExists(self, key):
        if self.checkIfExists(key) == False
            raise DataStoreError('Error: \'' + key + '\' does not exists.')


    # contexts methods

    def addContext(self, contextToken, context):
        '''
        Adds a context
        '''
        # check if the token provided is the same that in the context entity.
        self.raiseIfDifferent(contextToken, context['token'])
        # add token to the list of contexts
        self.add('contexts', contextToken)
        # add the context entity
        self.set(contextToken, context)

    def delContext(self, contextToken):
        '''
        Deletes a context
        '''
        # delete from list of tokens
        self.delete('contexts', contextToken)
        # delete entity
        self.delete(contextToken)

    def updateContext(self, contextToken, context):
        '''
        Updates a context with a new value
        '''
        # check if the token provided is the same that in the context entity.
        self.raiseIfDifferent(contextToken, context['token'])
        # set context entity
        self.set(contextToken, context)

    def getContext(self, contextToken):
        '''
        Gets the context entity
        '''
        self.get(contextToken)


    # images methods

    def addImage(self, imageToken, image, contextToken):
        '''
        Adds an image to a context
        '''
        # check if the token provided is the same that in the image entity.
        self.raiseIfDifferent(imageToken, image['token'])
        # get context
        context = self.getContext(contextToken)
        # add to the list of images in the context
        context['images'].append(imageToken)
        self.updateContext(context['token'], context)
        # add the image entity
        self.set(imageToken, image)

    def delImage(self, imageToken):
        '''
        Deletes an image
        '''
        # get image
        image = self.getImage(imageToken)
        # get context
        context = self.getContext(image['contextToken'])
        # remove reference to image in context
        context['images'].remove(imageToken)
        # remove image entity
        self.delete(imageToken)

    def updateImage(self, imageToken, image):
        '''
        Updates an image with a new value
        '''
        # check if the token provided is the same that in the image entity.
        self.raiseIfDifferent(imageToken, image['token'])
        # set entity
        self.raiseIfNotExists(imageToken)
        self.set(contextToken, context)

    def getImage(self, imageToken):
        '''
        Gets the image entity
        '''
        self.get(imageToken)


    # cluster methods



    # compositions methods
