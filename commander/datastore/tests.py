import unittest
from flask import Flask
from flask.ext.cache import Cache
from dataStore import DataStoreError, DataStore

app = Flask(__name__)
datastore = DataStore(app)

class setTests(unittest.TestCase):

    def test1(self):
        datastore.cache.clear()
        datastore.set('key', 'value')
        aux = datastore.cache.get('key')
        self.failUnless(aux == 'value')


class getTests(unittest.TestCase):

    def test1(self):
        datastore.cache.clear()
        datastore.cache.set('key', 'value')
        aux = datastore.get('key')
        self.failUnless(aux == 'value')

class addTests(unittest.TestCase):

    def test_empty_list(self):
        datastore.cache.clear()
        datastore.add('listKey', 'anElement')
        aux = datastore.get('listKey')
        self.failUnless(aux == ['anElement'])

    def test_not_empty_list(self):
        datastore.cache.clear()
        datastore.add('listKey', 'anElement')
        datastore.add('listKey', 'anotherElement')
        aux = datastore.get('listKey')
        self.failUnless(aux == ['anElement', 'anotherElement'])

class deleteTests(unittest.TestCase):

    def test_pair(self):
        datastore.cache.clear()
        datastore.cache.set('key', 'value')
        datastore.delete('key')
        aux = datastore.get('key')
        self.failUnless(aux == None)


    def test_element(self):
        datastore.cache.clear()
        datastore.cache.set('key', ['value1', 'value2'])
        datastore.delete('key', 'value1')
        aux = datastore.get('key')
        self.failUnless(aux == ['value2'])

class checkIfExistsTests(unittest.TestCase):

    def test_exists_key(self):
        datastore.cache.clear()
        datastore.cache.set('key', 'value')
        self.failUnless(datastore.checkIfExists('key'))


    def test_do_not_exists_key(self):
        datastore.cache.clear()
        self.failUnless(datastore.checkIfExists('key')==False)

    def test_exists_element(self):
        datastore.cache.clear()
        datastore.cache.set('key', ['value1', 'value2'])
        self.failUnless(datastore.checkIfExists('key', 'value1'))


    def test_do_not_exists_element(self):
        datastore.cache.clear()
        datastore.cache.set('key', ['value1', 'value2'])
        self.failUnless(datastore.checkIfExists('key', 'value3')==False)

def main():
    unittest.main()

if __name__ == '__main__':
    main()
