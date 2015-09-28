import os
import ssl
import settings
from threading import Thread
import subprocess
import re
import requests as req
import json

from controllers import errors
from files import createFile
import compose
import compose.config
from compose import project

# Importing docker library
def import_non_local(name, custom_name=None):
    """
    Tweak to import 'docker' module from docker-py inside de local 'docker' module.
    """
    import imp, sys

    custom_name = custom_name or name

    f, pathname, desc = imp.find_module(name, sys.path[1:])
    module = imp.load_module(custom_name, f, pathname, desc)
    if f != None:
        f.close()

    return module

dockerpy = import_non_local('docker', 'dockerpy')
# END: Importing docker library

def dockerClient(base_url=settings.DK_DEFAULT_TEST_HOST, cert_path=settings.DK_DEFAULT_TEST_HOST_CERTS):
    """
    Returns a docker-py client configured with URL and certs path. Set cert_path to None to disable TLS.
    """
    tls_config = None

    if cert_path != None:
        parts = base_url.split('://', 1)
        base_url = '%s://%s' % ('https', parts[1])

        client_cert = (os.path.join(cert_path, 'cert.pem'), os.path.join(cert_path, 'key.pem'))
        ca_cert = os.path.join(cert_path, 'ca.pem')

        tls_config = dockerpy.tls.TLSConfig(
            ssl_version=ssl.PROTOCOL_TLSv1,
            verify=True,
            assert_hostname=False,
            client_cert=client_cert,
            ca_cert=ca_cert,
        )

    timeout = settings.DK_CLIENT_TIMEOUT
    return dockerpy.Client(base_url=base_url, tls=tls_config, version='auto', timeout=timeout)

# Caching default dockerClient
defaultDockerClient = dockerClient()

def optionsFromClient(dk):
    """
    Extract command line options from docker-py client object
    """
    tls_flag = False
    # extract and convert host base_url from docker-py client
    host_url=dk.base_url
    # if host_url starts with https -> replace with tcp
    parts = host_url.split('://', 1)
    if parts[0] == 'https':
        host_url = '%s://%s' % ('tcp', parts[1])
        tls_flag = True

    if tls_flag:
        # extract cert path from docker-py client object
        certs=dk.cert   # [0] is 'cert.pem', [1] is 'key.pem'
        cacert=os.path.join(os.path.split(certs[0])[0], 'ca.pem')

        daemon_opts = "--host='"+host_url+"' --tlsverify=true --tlskey="+certs[1]+" --tlscert="+certs[0]+" --tlscacert="+cacert+" "
    else:
        daemon_opts = ""

    return daemon_opts


def checkDocker(dk=defaultDockerClient):
    """
    Checks the communication with Docker daemon. Returns True if ok, fail description if APIError.
    """
    try:
        dk.version()
        return True
    except Exception, e:
        return str(e)


def dockerVersion(dk=defaultDockerClient):
    """
    Returns information about the Docker daemon version.
    """
    return dk.version()


def dockerInfo(dk=defaultDockerClient):
    """
    Returns general information about docker daemon.
    """
    dk.info()


def purge(dk=defaultDockerClient):
    """
    Deletes all containers and images. Force if running. This operation is synchronous.
    Returns True if succefull, false if unsuccefull.
    """

    try:
        containers = dk.containers(all=True, quiet=True)
        for container in containers:
            dk.remove_container(container=container, v=True, force=True)

        images = dk.images(quiet=True)
        for image in images:
            dk.remove_image(image=image, force=True)

        return True

    except:
        return False


def pullImage(completeName, registry=None, dk=defaultDockerClient, imageFolder='/tmp'):
    image = completeName
    if registry:
        image = registry+'/'+completeName
    command = 'docker '+optionsFromClient(dk)+' pull '+image+' 1> '+ os.path.join(imageFolder, settings.FS_DEF_DOCKER_PULL_LOG) +' 2> '+ os.path.join(imageFolder, settings.FS_DEF_DOCKER_PULL_ERR_LOG)
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=imageFolder)

    response = ''
    for line in p.stdout.readlines():
        response+=line+os.linesep

    if p.wait() == 0:
        return True
    else:
        return False


def tagImage(orgName, destName, dk=defaultDockerClient, imageFolder='/tmp'):
    command = 'docker '+optionsFromClient(dk)+' tag -f '+orgName+" "+destName
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=imageFolder)

    response = ''
    for line in p.stdout.readlines():
        response+=line+os.linesep

    if p.wait() == 0:
        return True
    else:
        return False


def buildImage(datastore, contextToken, imageName, imageToken, dk=defaultDockerClient):
    # launch build
    # TODO: In the future, replace commandline docker API with docker-py client. The docker-py api for build do not support context path different from Dockerfile path.
    def __executeCommand__(command, cwd, pidfile):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        createFile(pidfile, str(p.pid))

        return p.wait()

    def __extractBaseImageName__(dockerfilepath):
        """
        Returns the name after the 'FROM' directive in the dockerfile (registry endpoint + provider + image name). Raises exception if not possible to extract the name.
        """
        res = None
        regEndpoint, provider, name = None, None, None
        with open(os.path.join(dockerfilepath, settings.FS_DEF_DOCKERFILE), "r") as f:
            for line in f:
                try:
                    res = re.search(r'^FROM\s*(.*)$', line).group(1)
                except AttributeError:
                    continue
                break
            f.close()

        if res:
            splitted = res.split("/")
            i = 0
            if len(splitted) == 3:
                regEndpoint=''.join(e for e in splitted[i] if (e.isalnum() or e == ':'))
                i = i+1
            if len(splitted) >= 2:
                provider=''.join(e for e in splitted[i] if e.isalnum())
                i = i+1
            name=''.join(e for e in splitted[i] if (e.isalnum() or e == ':'))
        return regEndpoint, provider, name

    def __buildThread__():
        err = None

        cwd =  os.path.join(settings.FS_BUILDS, contextToken)

        dockerfilepath = cwd
        dockerfilepath = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        dockerfilepath = os.path.join(dockerfilepath, imageName)

        pidfile = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_PID)
        try:
            daemon_opts = optionsFromClient(dk)

            # extract base name from dockerfile
            if err is None:
                if settings.DK_RG_SWITCH:
                    dkfRgEnd, dkfProv, dkfName = __extractBaseImageName__(dockerfilepath)
                    if not dkfName:
                        err = "Cannot extract image name from Dockerfile"
                    else:
                        pass

            # Pull image from registry
            if err is None:
                # if registry specified, pull from that. If not, try private reg.
                if dkfProv:
                    completeName = dkfProv+"/"+dkfName
                else:
                    completeName = dkfName
                if settings.DK_RG_SWITCH:
                    output = None
                    try:
                        if not dkfRgEnd:
                            dkfRgEnd = settings.DK_RG_ENDPOINT
                        output = pullImage(completeName, registry=dkfRgEnd, dk=dk, imageFolder=dockerfilepath)
                        # re-tag pulled image
                        if output:
                            if not tagImage(dkfRgEnd+'/'+completeName, completeName, dk=dk, imageFolder=dockerfilepath):
                                err = "Cannot tag '"+completeName+"'."
                    except Exception, e:
                        pass

                    if dkfRgEnd and dkfRgEnd!=settings.DK_RG_ENDPOINT and not output and not err:
                        err = "Cannot pull '"+completeName+"' from registry '"+dkfRgEnd+"'"

                # if not, try with public registry
                if err is None and not output:
                    try:
                        output = pullImage(completeName, registry=None, dk=dk, imageFolder=dockerfilepath)
                    except Exception, e:
                        pass

                    if not output:
                        err = "Cannot pull '"+completeName+"' from public nor private registry."


            # build
            if err is None:

                command = 'docker '+daemon_opts+' build -f '+ dockerfilepath+ '/'+ settings.FS_DEF_DOCKERFILE +' -t '+ datastore.getImage(imageToken)['tag'] +' . ' + '1> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_LOG) +' 2> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)

                if __executeCommand__(command, cwd, pidfile)!=0:
                    err = "Error while building"
                else:
                    createFile(os.path.join(dockerfilepath, "build_command"), command)

            if settings.DK_RG_SWITCH:
                # tag
                if err is None:
                    command = 'docker '+daemon_opts+' tag ' + datastore.getImage(imageToken)['tag']+' '+settings.DK_RG_ENDPOINT+'/'+datastore.getImage(imageToken)['tag']
                    if __executeCommand__(command, cwd, pidfile)!=0:
                        err = "Error tagging image. Maybe an image with the same name for this group already exists."
                    else:
                        pass
                    createFile(os.path.join(dockerfilepath, "tag_command"), command)

                # push
                if err is None:
                    command = 'docker '+daemon_opts+' push ' + settings.DK_RG_ENDPOINT+'/'+datastore.getImage(imageToken)['tag']
                    if __executeCommand__(command, cwd, pidfile)!=0:
                        err = "Error while pushing to registry"
                    else:
                        createFile(os.path.join(dockerfilepath, "push_command"), command)

            # Error case
            if err is not None:
                deleteImage(datastore, imageToken)
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG), err)
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '1')
            else:
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '0')


        except Exception, e:
            createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG), "Unexpected error in build thread.\n"+str(e))
            createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '1')

    thread = Thread(target = __buildThread__)
    thread.start()


def deleteImage(datastore, imageToken, dk=defaultDockerClient):
    try:
        daemon_opts = optionsFromClient(dk)
        # get tag of the docker image
        image = datastore.getImage(imageToken)
        context = datastore.getContext(image['context'])
        dockerImageTag = context['group']+'/'+image['imageName'].lower()

        # TODO: replace commandline docker API with docker-py client (fix docker host socket permission and TLS)
        cwd =  os.path.join(settings.FS_BUILDS, image['context'])
        cwd =  os.path.join(cwd, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
        cwd =  os.path.join(cwd, image['imageName'])

        command = 'docker '+daemon_opts+' rmi -f '+ dockerImageTag
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        retval = p.wait()

        return True
    except Exception, e:
        raise e
        return False


def deleteUntaggedImages(dk=defaultDockerClient):
    try:
        daemon_opts = optionsFromClient(dk)
        command = 'docker '+daemon_opts+' rmi -f  $(docker images | grep "^<none>" | awk "{print $3}")'
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        retval = p.wait()

        return True
    except Exception, e:
        raise e
        return False



def isDockerBuildRunning(contextToken, imageName):
    """
    Checks if the docker build process is still running. Returns True if the process still runs and False if the process is not running.
    """
    flag = os.path.join(settings.FS_BUILDS, contextToken)
    flag = os.path.join(flag, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    flag = os.path.join(flag, imageName)
    flag = os.path.join(flag, settings.FS_DEF_DOCKER_BUILD_FLAG)
    try:
        file = open(flag, 'r')
        file.close()
        return False
    except IOError:
        return True


def getBuildErrors(contextToken, imageName):
    """
    Retrieve errors in error building log. None if no errors.
    """
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)
    if os.stat(path).st_size == 0:
        return None
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def getBuildLog(contextToken, imageName):
    """
    Retrieve standard building log.
    """
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_LOG)
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def stopBuild(contextToken, imageName):
    """
    Stops the build process. Return True if could stop and False it not.
    """
    path = os.path.join(settings.FS_BUILDS, contextToken)
    path = os.path.join(path, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    path = os.path.join(path, imageName)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(path, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 9)
            return True
        except OSError:
            return False

def runComposition(datastore, token, dk=defaultDockerClient):
    # launch compose
    # TODO: control pulling errors
    def composeThread():
        cproject = ComposeProject(name=token, base_dir=os.path.join(settings.FS_COMPOSITIONS, token))
        # pull images
        cproject.pull()
        # run composition
        cproject.up()

    thread = Thread(target = composeThread)
    thread.start()


def buildBase(datastore, name, dk=defaultDockerClient):
    # launch build
    # TODO: In the future, replace commandline docker API with docker-py client. The docker-py api for build do not support context path different from Dockerfile path.
    def __executeCommand__(command, cwd, pidfile):
        p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=cwd)

        response = ''
        for line in p.stdout.readlines():
            response+=line+os.linesep

        createFile(pidfile, str(p.pid))

        return p.wait()

    def __buildThread__():
        err = None
        cwd = os.path.join(settings.FS_BASES, name)

        dockerfilepath = cwd

        pidfile = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_PID)

        try:
            daemon_opts = optionsFromClient(dk)
            tag = settings.DK_DEFAULT_BASE_PROVIDER + '/' + name

            # build
            if err is None:
                command = 'docker '+daemon_opts+' build -f '+ dockerfilepath+'/'+ settings.FS_DEF_DOCKERFILE +' -t '+ tag +' . ' + '1> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_LOG) +' 2> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)

                if __executeCommand__(command, cwd, pidfile)!=0:
                    err = "Error while building"
                else:
                    createFile(os.path.join(dockerfilepath, "build_command"), command)

            if settings.DK_RG_SWITCH:
                # tag
                if err is None:
                    command = 'docker '+daemon_opts+' tag ' + tag +' '+ settings.DK_RG_ENDPOINT +'/'+ tag
                    if __executeCommand__(command, cwd, pidfile)!=0:
                        err = "Error tagging image. Maybe an image with the same name for this group already exists."
                    else:
                        createFile(os.path.join(dockerfilepath, "tag_command"), command)

                # push
                if err is None:
                    command = 'docker '+daemon_opts+' push ' + settings.DK_RG_ENDPOINT +'/'+ tag
                    if __executeCommand__(command, cwd, pidfile)!=0:
                        err = "Error while pushing to registry"
                    else:
                        createFile(os.path.join(dockerfilepath, "push_command"), command)

            # Error case
            if err is not None:
                deleteImage(datastore, imageToken)
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG), err)
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '1')
            else:
                createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '0')

        except Exception, e:
            createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG), "Unexpected error in build thread."+str(e))
            createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_FLAG), '1')


    thread = Thread(target = __buildThread__)
    thread.start()

def deleteBaseImage(name):
    # TODO
    pass

def stopBaseImage(name):
    # TODO
    pass

def isBaseBuildRunning(name):
    """
    Checks if the docker build process is still running. Returns True if the process still runs and False if the process is not running.
    """
    flag = os.path.join(settings.FS_BASES, name)
    flag = os.path.join(flag, settings.FS_DEF_DOCKER_BUILD_FLAG)
    try:
        file = open(flag, 'r')
        file.close()
        return False
    except IOError:
        return True

def getBaseBuildLog(name):
    """
    Retrieve standard building log.
    """
    path = os.path.join(settings.FS_BASES, name)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_LOG)
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

def getBaseBuildErrors(name):
    """
    Retrieve errors in error building log. None if no errors.
    """
    path = os.path.join(settings.FS_BASES, name)
    path = os.path.join(path, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)
    if os.stat(path).st_size == 0:
        return None
    content = ''
    with open(path, 'r') as content_file:
        content = content_file.read()
    return content

class ComposeProject():
    def __init__(self, name, base_dir, filename='docker-compose.yml', dockerClient=defaultDockerClient, default_registry=None):
        self.dockerClient = dockerClient
        self.service_dicts = compose.config.load(compose.config.find(base_dir, filename))
        self.project = project.Project.from_dicts(name, self.service_dicts, self.dockerClient)
        self.default_registry = default_registry

    def pull(self):
        try:
            # Open file that will store the pull log
            pull_log=open(settings.FS_DEF_DOCKER_COMPOSE_PULL_LOG, 'w')

            # Create file that marks the status of the pulling (exit code)
            pull_code = open(settings.FS_DEF_DOCKER_COMPOSE_PULL_CODE, 'w')
            pull_code.write("")
            pull_code.close()

            # Call project pull. It will fill the log file
            self.project.pull(default_registry=default_registry, out_stream=pull_log)

            ## TODO: add logic here to check if images has been pulled or not.

            # Set exit code
            pull_code = open(settings.FS_DEF_DOCKER_COMPOSE_PULL_CODE, 'w')
            pull_code.write("0")
            pull_code.close()

        except:
            # Set exit code
            pull_code = open(settings.FS_DEF_DOCKER_COMPOSE_PULL_CODE, 'w')
            pull_code.write("1")
            pull_code.close()

        finally:
            pull_log.close()
            pull_code.close()


    def up(self):
        self.project.up()

def imageInRegistry(name):
    """
    Returns True if the image exists on registry, False if not.
    """
    res = req.get('https://'+settings.DK_RG_ENDPOINT+'/v2/'+name+'/tags/list', \
            verify=settings.DK_RG_CA)
    if res.status_code == 200:
        return True
    elif res.status_code == 404:
        return False
    else:
        raise Exception("Response not expected. Maybe something is bad with registry.")
