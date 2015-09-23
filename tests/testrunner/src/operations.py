import os
import requests as req
import settings as s

def postBase(name, dockerfilePath):
    dockerfile = open(dockerfilePath,'rb')
    return req.post(s.COMMANDER_URL+'/builder/images/bases', \
           data = {'imageName':name}, \
           files = {'dockerfile':dockerfile})

def getBase(name):
    return req.get(s.COMMANDER_URL+'/builder/images/bases/'+name)

def getRegistryImage(name):
    return req.get(s.REGISTRY_URL+'/v2/'+name+'/tags/list', \
            verify=s.REGISTRY_CA)

def purgeCrane():
    return req.get(s.COMMANDER_URL+'/extra/purge')

def assertStatusCode(res, statusCode, text='NOT GOOD'):
    assert res.status_code == statusCode, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": HTTP status code returned is "+ str(res.status_code) + \
        ",different from " + str(statusCode)

def assertStatus(res, desiredStatus, text='NOT GOOD'):
    assert res.json()['status'] == desiredStatus, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": 'status' returned is different from '"+ desiredStatus +"'"
