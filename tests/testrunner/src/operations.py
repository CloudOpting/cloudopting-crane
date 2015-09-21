import os
import requests as req
import settings as s

def postBase(name, dockerfilePath):
    dockerfile = open(dockerfilePath=,'rb')
    return req.post(s.COMMANDER_URL+'/builder/images/bases', \
           data = {'imageName':name}, \
           files = {'dockerfile':dockerfile})

def getBase(name):
    return req.get(s.COMMANDER_URL+'/builder/images/bases/'+name)

def getRegistryImage(name):
    return req.get(s.REGISTRY_URL+'/v2/'+name+'/tags/list', \
            verify='/var/tests/certs/registry-ca.crt')
