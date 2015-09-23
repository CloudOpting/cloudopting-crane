#!/usr/bin/python

import pytest
import os
import requests as req
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

        res = op.waitWhileStatus(op.getBase, imageName, \
            text="Error while asking base status")
        op.assertStatus(res, 'finished', \
            "Error in base image built proccess")


        # check base
        res = op.getRegistryImage(s.DEF_BASE_PROVIDER+'/'+imageName)
        op.assertStatusCode(res, 200, 'Base image not saved to registry')

        # build context
        group='example'
        res = op.postContext(group, os.path.join(resources, 'img/puppetfile'))

        op.assertStatusCode(res, 200, text='Error creating context')
        op.assertStatus(res, 'building', text='Error creating context')

        contextToken = res.json()['token']

        res = op.waitWhileStatus(op.getContext, contextToken, \
            text="Error while asking context status")
        op.assertStatus(res, 'finished', \
            "Error in context built proccess")


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
        # TODO: not implemented yet
        # check stopped
        # TODO: not implemented yet
        # remove from cluster
        # TODO: not implemented yet
        # check removed
        # TODO: not implemented yet
        # remove from crane
        # TODO: not implemented yet
        # check removed from registry
        # TODO: not implemented yet
        # check removed from engine cache
        # TODO: not implemented yet
