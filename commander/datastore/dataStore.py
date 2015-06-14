from flask.ext.cache import Cache

class DataStoreError(Exception):
    pass

class DataStore:
    def __init__(self, app):
        self.app = app
        self.cache = Cache(app, config={'CACHE_TYPE':'simple'})

    # generic methods

    def clear(self):
        '''
        Clears all the information in the datastore
        '''
        self.cache.clear()

    def set(self, key, value):
        '''
        Sets value to a key
        '''
        self.cache.set(key, value)

    def add(self, listKey, value):
        '''
        Adds a item to a list
        '''
        aux = self.cache.get(listKey)
        if aux == None:
            aux = []
        aux.append(value)
        self.cache.set(listKey, aux)

    def get(self, key):
        '''
        Gets a value from it key
        '''
        return self.cache.get(key)

    def delete(self, key, element=None):
        '''
        Deletes a key-value pair or an element in a list (if element argument is given)
        '''
        if element==None:
            self.cache.delete(key)
        else:
            aux = self.cache.get(key)
            aux.remove(element)
            self.cache.set(key, aux)


    def checkIfExists(self, key, element=None):
        '''
        Checks if a key is defined or if an element exists in a list (if element is given)
        '''
        if element==None:
            if self.cache.get(key) == None:
                return False
            return True
        else:
            aux = self.cache.get(key)
            return element in aux

    def raiseIfDifferent(self, a, b):
        if a != b:
            raise DataStoreError('Error: \'' + a + '\' and \'' + b + '\' are different.')

    def raiseIfNotExists(self, key):
        if self.checkIfExists(key) == False:
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
        return self.get(contextToken)

    def getContexts(self):
        '''
        Gets the list with all the context tokens.
        '''
        return self.get('contexts')

    # images methods

    def addImage(self, contextToken, imageToken, image):
        '''
        Adds an image to a context. Raises DataStoreError if image is already associated with the context.
        '''
        # check if the token provided is the same that in the image entity.
        self.raiseIfDifferent(imageToken, image['token'])
        # get context
        context = self.getContext(contextToken)
        # add to the list of images in the context
        if imageToken in context['images']:
            raise DataStoreError('\'' + imageToken + '\' already exists.')
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
        self.set(imageToken, image)

    def getImage(self, imageToken):
        '''
        Gets the image entity
        '''
        return self.get(imageToken)


    # cluster methods

    def addCluster(self, clusterToken, cluster):
        '''
        Adds a cluster
        '''
        # check if the token provided is the same that in the cluster entity.
        self.raiseIfDifferent(clusterToken, cluster['token'])
        # add to the list of clusters
        self.add('clusters', clusterToken)
        # add the cluster entity
        self.set(clusterToken, cluster)

    def delCluster(self, clusterToken):
        '''
        Deletes a cluster
        '''
        # delete from list of clusters
        self.delete('clusters', clusterToken)
        # delete entity
        self.delete(clusterToken)

    def updateCluster(self, clusterToken, cluster):
        '''
        Updates a cluster with a new value
        '''
        # check if the token provided is the same that in the cluster entity.
        self.raiseIfDifferent(clusterToken, cluster['token'])
        # set cluster entity
        self.set(clusterToken, cluster)

    def getCluster(self, clusterToken):
        '''
        Gets the cluster entity
        '''
        return self.get(clusterToken)


    # compositions methods

    def addComposition(self, compositionToken, composition):
        '''
        Adds a composition
        '''
        # check if the token provided is the same that in the composition entity.
        self.raiseIfDifferent(compositionToken, composition['token'])
        # add to the list of compositions
        self.add('compositions', compositionToken)
        # add the composition entity
        self.set(compositionToken, composition)

    def delComposition(self, compositionToken):
        '''
        Deletes a composition
        '''
        # delete from list of compositions
        self.delete('compositions', compositionToken)
        # delete entity
        self.delete(compositionToken)

    def updateComposition(self, compositionToken, composition):
        '''
        Updates a composition with a new value
        '''
        # check if the token provided is the same that in the composition entity.
        self.raiseIfDifferent(compositionToken, composition['token'])
        # set composition entity
        self.set(compositionToken, composition)

    def getComposition(self, compositionToken):
        '''
        Gets the composition entity
        '''
        return self.get(compositionToken)
