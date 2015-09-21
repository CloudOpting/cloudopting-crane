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
    def test_webapp(self):
        """Simple webapp in remote pre-provisioned docker host"""

        # Directory where resources are stored
        resources = os.path.join(s.TEST_RES, 'test-1')

        # build base
        res = op.buildBase('ubuntubase', \
                os.path.join(resources, 'bases/ubuntubase'))

        assert res.status_code == 200, \
            res.request.method+": "+res.request.path_url+": "+ \
            "HTTP status code returned is different from 200"

        assert res.json()['status'] == 'building', \
            res.request.method+": "+res.request.path_url+": "+ \
            "'status' returned is different from 'building'"

        while True: # wait until image is finished
            res = op.getBase(name)
            assert res.status_code == 200, \
                res.request.method+": "+res.request.path_url+": "+ \
                "HTTP status code returned is different from 200"

            if res.json()['status'] == 'building':
                time.sleep(5)
                continue

            assert res.json()['status'] == 'finished', \
                res.request.method+": "+res.request.path_url+": "+ \
                "'status' returned is different from 'finished'"


        # check base
        res = op.getRegistryImage('cloudopting/ubuntubase')

        assert res.status_code == 200, \
            res.request.method+": "+res.request.path_url+": "+ \
            "HTTP status code returned is different from 200."+ \
            "Base image not saved to registry."

        


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
