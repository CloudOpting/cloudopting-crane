import os
import requests as req
import settings as s
import time

def purgeCrane():
    return req.get(s.COMMANDER_URL+'/extra/purge')


def postBase(name, dockerfilePath):
    dockerfile = open(dockerfilePath,'rb')
    res = req.post(s.COMMANDER_URL+'/builder/images/bases', \
           data = {'imageName':name}, \
           files = {'dockerfile':dockerfile})

    dockerfile.close()
    return res


def getBase(name):
    return req.get(s.COMMANDER_URL+'/builder/images/bases/'+name)


def getRegistryImage(name):
    return req.get(s.REGISTRY_URL+'/v2/'+name+'/tags/list', \
            verify=s.REGISTRY_CA)


def postContext(group, puppetfilePath):
    puppetfile = open(puppetfilePath,'rb')
    res = req.post(s.COMMANDER_URL+'/builder/contexts', \
           data = {'group':group}, \
           files = {'puppetfile':puppetfile})

    puppetfile.close()
    return res


def getContext(contextToken):
    return req.get(s.COMMANDER_URL+'/builder/contexts/'+contextToken)


def postImage(contextToken, imageName, dockerfilePath=None, \
        puppetmanifestPath=None):
    dockerfile = open(dockerfilePath,'rb') if dockerfilePath!=None else None
    puppetfile = open(puppetfilePath,'rb') if puppetfilePath!=None else None
    files= {}
    if dockerfile!=None:
        files['dockerfile']=dockerfile
    if puppetfile!=None:
        files['puppetfile']=puppetfile

    res = req.post(s.COMMANDER_URL+'/builder/images', \
            data = {'contextReference': contextToken, 'imageName': imageName}, \
            files = files)

    if dockerfile!=None:
        dockerfile.close()
    if puppetfile!=None:
        puppetfile.close()
    return res

def getImage(imageToken):
    return req.get(s.COMMANDER_URL+'/builder/images/'+imageToken)

def postCluster(endpoint, apiVersion=None, clientCertPath=None, \
        clientKeyPath=None, clientCaPath=None):
    clientCert = open(clientCertPath,'rb') if clientCertPath!=None else None
    clientKey = open(clientKeyPath,'rb') if clientKeyPath!=None else None
    clientCa = open(clientCaPath,'rb') if clientCaPath!=None else None
    files= {}
    if clientCert!=None:
        files['clientCert']=clientCert
    if clientKey!=None:
        files['clientKey']=clientKey
    if clientCa!=None:
        files['clientCa']=clientCa

    res = req.post(s.COMMANDER_URL+'/cluster/provisionedSingleMachine', \
            data = {'contextReference': contextToken, 'imageName': imageName}, \
            files = files)

    if clientCert!=None:
        clientCert.close()
    if clientKey!=None:
        clientKey.close()
    if clientCa!=None:
        clientCa.close()
    return res


def getCluster(clusterToken):
    return req.get(s.COMMANDER_URL+'/cluster/'+clusterToken)


def postComposition(clusterToken, composefilePath):
    composefile = open(composefilePath,'rb')
    res = req.post(s.COMMANDER_URL+'/composer', \
           data = {'clusterToken':clusterToken}, \
           files = {'composefile':composefile})

    composefile.close()
    return res


def waitWhileStatus(getStatusFunc, token, status='building', period=5, text='NOT GOOD'):
    while True: # wait process to finish
        res = getStatusFunc(token)
        assertStatusCode(res, 200, text)

        if res.json()['status'] == status:
            time.sleep(period)
            continue

        break

    return res


def assertStatusCode(res, statusCode, text='NOT GOOD'):
    assert res.status_code == statusCode, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": HTTP status code returned is "+ str(res.status_code) + \
        ",different from " + str(statusCode)

def assertStatus(res, desiredStatus, text='NOT GOOD'):
    assert res.json()['status'] == desiredStatus, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": 'status' returned is different from '"+ desiredStatus +"'"
