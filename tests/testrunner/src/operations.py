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


def postImage(contextToken, imageName, base=None, dockerfilePath=None, \
        puppetmanifestPath=None):
    dockerfile = open(dockerfilePath,'rb') if dockerfilePath!=None else None
    puppetmanifest = open(puppetmanifestPath,'rb') if puppetmanifestPath!=None else None
    files= {}
    data = {'contextReference': contextToken, 'imageName': imageName}
    if dockerfile!=None:
        files['dockerfile']=dockerfile
    if puppetmanifest!=None:
        files['puppetmanifest']=puppetmanifest
    if base!=None:
        data['base']=str(base)

    res = req.post(s.COMMANDER_URL+'/builder/images', data=data, files=files)

    if dockerfile!=None:
        dockerfile.close()
    if puppetmanifest!=None:
        puppetmanifest.close()
    return res

def getImage(imageToken):
    return req.get(s.COMMANDER_URL+'/builder/images/'+imageToken)

def postCluster(endpoint, apiVersion=None, clientCertPath=None, \
        clientKeyPath=None, caPath=None):
    clientCert = open(clientCertPath,'rb') if clientCertPath!=None else None
    clientKey = open(clientKeyPath,'rb') if clientKeyPath!=None else None
    ca = open(caPath,'rb') if caPath!=None else None
    files= {}
    if clientCert!=None:
        files['clientCert']=clientCert
    if clientKey!=None:
        files['clientKey']=clientKey
    if ca!=None:
        files['ca']=ca

    res = req.post(s.COMMANDER_URL+'/cluster/provisionedSingleMachine', \
            data = {'contextReference': contextToken, 'imageName': imageName}, \
            files = files)

    if clientCert!=None:
        clientCert.close()
    if clientKey!=None:
        clientKey.close()
    if ca!=None:
        ca.close()
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


def waitWhileStatus(getStatusFunc, token, status='building', period=5, \
        text='NOT GOOD'):
    while True: # wait process to finish
        res = getStatusFunc(token)
        assertStatusCode(res, 200, text)
        if res.json()['status'] == status:
            time.sleep(period)
            continue
        break

    return res


def buildImageAndAssert(group, name, contextToken, base=None, \
        dockerfilePath=None, puppetmanifestPath=None):
    # check if image already exists in the registry
    completeName=group+'/'+name
    res = getRegistryImage(completeName)
    assertStatusCode(res, 404, \
     "Cannot assure '"+completeName+"' image is not already on the registry.")

    # launch build
    res = postImage(contextToken, name, base, dockerfilePath, puppetmanifestPath)
    text = "Error posting image '"+name+"'"
    assertStatusCode(res, 200, text)
    assertStatus(res, 'building', text=text)
    # wait until finish
    text = "Error building image '"+completeName+"'"
    aux = "token:"+res.json()['token']
    res = waitWhileStatus(getImage, res.json()['token'], status='building', text=text)
    assertStatusCode(res, 200, text)
    assertStatus(res, 'finished', text=text)

    return res


def assertStatusCode(res, statusCode, text='NOT GOOD'):
    assert res.status_code == statusCode, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": HTTP status code returned is "+ str(res.status_code) + \
        ",different from " + str(statusCode)+".\nRes content: "+res.content+ \
        "\nRequest: "+str(res.request.body)

def assertStatus(res, desiredStatus, text='NOT GOOD'):
    assert res.json()['status'] == desiredStatus, \
        res.request.method+": "+res.request.path_url+": "+ \
        text + ": 'status' returned is different from '"+ desiredStatus +"'\n"\
        +".\nResp content: "+res.content+ "\nRequest content: "+\
        str(res.request.body)
