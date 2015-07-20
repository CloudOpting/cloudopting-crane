import sys
sys.path.append('..') # fix to enable unittest (when launched in the test directory) to import settings.py which is in the pather directory.

import unittest

import settings

from flask import Flask
from datastore.dataStore import DataStore
from toolbox import files, docker
from controllers.builder import builderOps

from werkzeug.datastructures import FileStorage

class ControllerTestCase(unittest.TestCase):
    def setUp(self):
        # prepare filesystem
        settings.FS_ROOT = '/var/crane_tests/'   # overwrite root path
        settings.FS_BUILDS = settings.FS_ROOT + 'builds/'
        settings.FS_COMPOSITIONS = settings.FS_ROOT + 'compositions/'
        files.purgeWorkdir()

        # prepare docker
        chk = docker.checkDocker()
        if chk!=True:   # Check docker avaliability
            raise Exception("Cannot communicate with Docker daemon:" + chk)

        # start flask and datastore
        self.app = Flask(__name__)
        self.ds = DataStore(self.app)


    def tearDown(self):
        # purge filesystem
        files.purgeWorkdir()

        # purge docker
        files.purgeWorkdir()


class BuilderTestCase(ControllerTestCase):

    def test_listContexts_empty(self):
        response = builderOps.contextList(self.ds)
        self.assertEqual({"contexts":[]}, response, "wrong response")

    def test_listContexts_notEmpty(self):
        response = builderOps.newContext(datastore = self.ds, puppetfile=FileStorage(stream=open('testResources/Puppetfile', 'r')))
        token = response['token']
        self.fail(response)
        self.assertIsNotNone(token, "cannot create context")
        self.assertEqual({"contexts":[token]}, response, "wrong response")

    @unittest.skip("skipping for the momment")
    def test_newContextBad(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newContext_Right(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newContext_Right_Named(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_checkContext_NotStarted(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_checkContext_Started(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_deleteContext_NoExists(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_deleteContext_Exists_Building(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_deleteContext_Exists_Finished(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newImage_NoContext(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newImage_ErroneousDockerfile(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newImage_ErroneousPuppetfile(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newImage_NoName(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_newImage_Correct(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_checkImage_NotStarted(self):
        self.self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_checkImage_Started(self):
        self.self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_deleteImage_Exists_Finished(self):
        self.fail("shouldn't happen")

    @unittest.skip("skipping for the momment")
    def test_deleteImage_Exists_Building(self):
        self.fail("shouldn't happen")
