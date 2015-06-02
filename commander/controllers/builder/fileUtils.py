import settings
import os
import shutil

def createDir(token):
    os.makedirs(settings.FS_BUILDS+token, 0775)

def deleteDir(token):
    path = os.path.join(settings.FS_BUILDS, token)
    shutil.rmtree(path, ignore_errors=True)

def savePuppetfile(token, puppetfile):
    path = os.path.join(settings.FS_BUILDS, token)
    path = os.path.join(path, settings.FS_DEF_PUPPETFILE)
    puppetfile.save(path)
