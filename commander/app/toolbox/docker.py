import os
import ssl
import settings
from threading import Thread
import subprocess


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

    def __buildThread__():
        err = None
        try:

            cwd =  os.path.join(settings.FS_BUILDS, contextToken)

            dockerfilepath = cwd
            dockerfilepath = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
            dockerfilepath = os.path.join(dockerfilepath, imageName)

            pidfile = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_PID)

            daemon_opts = optionsFromClient(dk)

            # build
            if err is None:

                command = 'docker '+daemon_opts+' build -f '+ dockerfilepath+ '/'+ settings.FS_DEF_DOCKERFILE +' -t '+ 'default/'+datastore.getImage(imageToken)['imageName'] +' . ' + '1> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_LOG) +' 2> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)

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

        except Exception, e:
            createFile(os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG), "Unexpected error in build thread.")

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
    pidpath = os.path.join(settings.FS_BUILDS, contextToken)
    pidpath = os.path.join(pidpath, settings.FS_DEF_DOCKER_IMAGES_FOLDER)
    pidpath = os.path.join(pidpath, imageName)
    pidpath = os.path.join(pidpath, settings.FS_DEF_DOCKER_BUILD_PID)
    try:
        file = open(pidpath, 'r')
    except IOError:
        return True
    pid = int(file.read(10));
    if pid > 1:
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            pass
    return False


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
        try:
            cwd = os.path.join(settings.FS_BASES, name)

            dockerfilepath = cwd

            pidfile = os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_PID)

            daemon_opts = optionsFromClient(dk)
            tag = settings.DK_DEFAULT_BASE_PROVIDER + '/' + name

            # build
            if err is None:
                command = 'docker '+daemon_opts+' build -f '+ dockerfilepath+ '/'+ settings.FS_DEF_DOCKERFILE +' -t '+ tag +' . ' + '1> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_LOG) +' 2> '+ os.path.join(dockerfilepath, settings.FS_DEF_DOCKER_BUILD_ERR_LOG)

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

        except Exception, e:
            createFile(os.path.join('/tmp/', settings.FS_DEF_DOCKER_BUILD_ERR_LOG), "Unexpected error in build thread.")

    thread = Thread(target = __buildThread__)
    thread.start()

def deleteBaseImage(datastore, name):
    # TODO
    pass

def stopBaseImage(datastore, name):
    # TODO
    pass

def isBaseBuildRunning(datastore, name):
    # TODO
    pass

def getBaseBuildLog(datastore, name):
    # TODO
    pass

def getBaseBuildLog(datastore, name):
    # TODO
    pass

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
