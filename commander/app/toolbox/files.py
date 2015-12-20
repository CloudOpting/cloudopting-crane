import settings
import os
import shutil

# Context related operations

def createContextDir(token):
    path = os.path.join(settings.FS_BUILDS, token)
    os.makedirs(path, 0775)

def deleteContextDir(token):
    path = os.path.join(settings.FS_BUILDS, token)
    shutil.rmtree(path, ignore_errors=True)

def savePuppetfile(token, puppetfile):
    path = os.path.join(settings.FS_BUILDS, token)
    path = os.path.join(path, settings.FS_DEF_PUPPETFILE)
    puppetfile.save(path)

# Base images related operations
def createBaseDir(name):
    path = os.path.join(settings.FS_BASES, name)
    os.makedirs(path, 0775)

def deleteBaseDir(name):
    path = os.path.join(settings.FS_BASES, name)
    shutil.rmtree(path, ignore_errors=True)

def saveBaseDockerfile(name, dockerfile):
    path = os.path.join(settings.FS_BASES, name)
    path = os.path.join(path, settings.FS_DEF_DOCKERFILE)
    dockerfile.save(path)

def createBaseDockerfile(contextToken, imageName, baseName):
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKERFILE)
    content='#Autogenerated Dockerfile\nFROM '+baseName+"\n" \
            +"# Add puppet modules:\n" \
            +"ADD modules /tmp/modules\n" \
            +"# Add manifest to apply\n" \
            +"ADD images/"+imageName+"/manifest.pp /tmp/manifest.pp\n" \
            +"# Apply manifest\n" \
            +"RUN puppet apply --modulepath=/tmp/modules /tmp/manifest.pp\n"

    createFile(path, content)

# Image related operations

def createImageDir(contextToken, imageName):
    path = os.path.join(settings.FS_BUILDS, contextToken)
    if os.path.isdir(path):
        path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        if not os.path.exists(path):
            os.makedirs(path, 0775)
        path = os.path.join(path, imageName)
        os.makedirs(path, 0775)
    else:
        raise Exception("Context directory not found")

def deleteImageDir(contextToken, imageName):
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    shutil.rmtree(path, ignore_errors=True)

def saveDockerfile(contextToken, imageName, dockerfile):
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKERFILE)
    dockerfile.save(path)

def savePuppetManifest(contextToken, imageName, puppetmanifest, filename=None):
    if filename:
        path = os.path.join(settings.FS_BUILDS, contextToken)
        path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        path = os.path.join(path, filename)
    else:
        path = os.path.join(settings.FS_BUILDS, contextToken)
        path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        path = os.path.join(path, imageName)
        path = os.path.join(path, settings.FS_DEF_PUPPETMANIFEST)

    puppetmanifest.save(path)

# Cluster related operations

def createClusterDir(token):
    path = os.path.join(settings.FS_CLUSTERS, token)
    os.makedirs(path, 0775)

def deleteClusterDir(token):
    path = os.path.join(settings.FS_CLUSTERS, token)
    shutil.rmtree(path, ignore_errors=True)

# Composer related operations

def saveComposeFile(token, composefile):
    if not os.path.exists(settings.FS_COMPOSITIONS):
        os.makedirs(settings.FS_COMPOSITIONS, 0775)
    path = os.path.join(settings.FS_COMPOSITIONS, token)
    os.makedirs(path, 0775)
    path = os.path.join(path, settings.FS_DEF_COMPOSEFILE)
    composefile.save(path)

def deleteComposeFile(token):
    path = os.path.join(settings.FS_COMPOSITIONS, token)
    os.remove(path)


# Common file operations

def createFile(path, content):
    fo = open(path, "wb")
    fo.write(content);
    fo.close()

def purgeWorkdir():
    if os.path.exists(settings.FS_BUILDS):
        shutil.rmtree(settings.FS_BUILDS)
    if os.path.exists(settings.FS_CLUSTERS):
        shutil.rmtree(settings.FS_CLUSTERS)
    if os.path.exists(settings.FS_COMPOSITIONS):
        shutil.rmtree(settings.FS_COMPOSITIONS)
