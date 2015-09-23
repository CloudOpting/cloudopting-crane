#!/usr/bin/python

import pytest
import os
import requests as req
import time
import settings as s
import operations as op

class TestsBasic:
    def test_isalive(self):
        """Check if Crane is alive"""
        res = req.get(s.COMMANDER_URL+'/extra/alive')
        assert res.status_code == 200, "Crane is not alive"

    def test_builtinCheck(self):
        """Check Crane built-in check result"""
        res = req.get(s.COMMANDER_URL+'/extra/check')
        assert res.json()['docker'] == 'correct', \
            "Crane connection with docker is not 'correct'"

class TestsCompleteCycle:
    """Complete cycle tests: build, save, and execution"""

    @classmethod
    def setup_class(cls):
        # delete engine containers, images and crane data
        res = op.purgeCrane()
        errText = "Cannot purge Crane"
        op.assertStatusCode(res, 200, errText)
        op.assertStatus(res, 'finished', errText)

    @classmethod
    def teardown_class(cls):
        pass

    def test_webapp(self):
        """Simple webapp in remote pre-provisioned docker host"""

        # Directory where resources are stored
        resources = os.path.join(s.TEST_RES, 'test-1')

        # Name of the image
        imageName = 'ubuntubase'

        # make sure that image do not exist in registry
        res = op.getRegistryImage(s.DEF_BASE_PROVIDER+'/'+imageName)
        #op.assertStatusCode(res, 404, \
        #    "Cannot assure base image is not already on the registry.")

        # build base
        res = op.postBase(imageName, \
                os.path.join(resources, 'bases/'+imageName))
        errText = "Error in build base request"
        op.assertStatusCode(res, 200, errText)
        op.assertStatus(res, 'building', errText)

        while True: # wait image built process to finish
            res = op.getBase(imageName)
            op.assertStatusCode(res, 200, "Error while asking base status")

            if res.json()['status'] == 'building':
                time.sleep(5)
                continue

            op.assertStatus(res, 'finished', \
                "Error in base image built proccess")

            break


        # check base
        res = op.getRegistryImage(s.DEF_BASE_PROVIDER+'/'+imageName)
        op.assertStatusCode(res, 200, 'Base image not saved to registry')

        # build context


        # check context
        # build image 1
        # check image 1
        # build image 2
        # check image 2
        # build image 3
        # check image 3
        # create cluster
        # check cluster
        # run composition
        # check functionality
        # stop composition
        # check stopped
        # remove from cluster
        # check removed
        # remove from crane
        # check removed from registry
        # check removed from engine cache
