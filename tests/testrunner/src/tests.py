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

        ## Directory where resources are stored
        resources = os.path.join(s.TEST_RES, 'test-1')
        group = 'test1'

        # build base
        ## Name of the base image
        baseName = 'ubuntubase'

        ## make sure that image do not exist in registry
        res = op.getRegistryImage(s.DEF_BASE_PROVIDER+'/'+baseName)
        op.assertStatusCode(res, 404, \
            "Cannot assure base image is not already on the registry.")

        res = op.postBase(baseName, \
                os.path.join(resources, 'bases/'+baseName))
        errText = "Error in build base request"
        op.assertStatusCode(res, 200, errText)
        op.assertStatus(res, 'building', errText)

        res = op.waitWhileStatus(op.getBase, baseName, \
            text="Error while asking base status")
        op.assertStatus(res, 'finished', \
            "Error in base image built proccess")


        # check base
        res = op.getRegistryImage(s.DEF_BASE_PROVIDER+'/'+baseName)
        op.assertStatusCode(res, 200, 'Base image not saved to registry')

        # build context
        res = op.postContext(group, os.path.join(resources, 'img/puppetfile'))

        op.assertStatusCode(res, 200, text='Error creating context')
        op.assertStatus(res, 'building', text='Error creating context')

        contextToken = res.json()['token']

        res = op.waitWhileStatus(op.getContext, contextToken, \
            text="Error while asking context status")
        op.assertStatus(res, 'finished', \
            "Error in context built proccess")

        # build redis
        op.buildImageAndAssert(group, 'redis', contextToken, \
            dockerfilePath=os.path.join(resources, 'img/redis/Dockerfile'))

        # build webconsumer
        op.buildImageAndAssert(group, 'webconsumer', contextToken, \
            dockerfilePath=os.path.join(resources, \
                    'img/webconsumer/Dockerfile'), \
            puppetmanifestPath=os.path.join(resources, \
                    'img/webconsumer/manifest.pp' ))

        # build webproducer
        op.buildImageAndAssert(group, 'webproducer', contextToken, \
            base=baseName,
            puppetmanifestPath=os.path.join(resources, \
                    'img/webproducer/manifest.pp' ))

        # create cluster
        res = op.postCluster(HOST_ENDPOINT, \
            clientCertPath=s.HOST_CERT, clientKeyPath=s.HOST_KEY, \
            caPath=s.HOST_CA)
        text='Error submitting cluster'
        clusterToken = res.json()['token']
        op.assertStatusCode(res, 200, text)
        op.assertStatus(res, 'ready', text)

        # run composition
        res = op.postComposition(clusterToken, \
                os.path.join(resources, 'run/compose.yml'))
        text='Error deploying composition'
        op.assertStatusCode(res, 200, text)
        op.assertStatus(res, 'ready', text)


        # check functionality
        ## TODO: call both servers to check if the service works

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
