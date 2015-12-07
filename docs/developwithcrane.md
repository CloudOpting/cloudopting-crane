# Use crane in development

This guide shows how crane can be used to help in the service migration process.

# Overview and general concepts

__Token__

Almost every operation is asynchronous. You have to do the request and after check the status.

The request gives you an operation identifier. This is call a token.

Tokens also identifies the resource, so it can be used as parameter in other operations.

The are several types:

- _context token_: identifies a context. Starts with `CT`.
- _build token_: identifies a build process. Follows the format `<context token>-<imagename>`.
- _cluster token_: identifies a cluster. Starts with `CL`.
- _composition token_: identifies a composition deploy process. Starts with `CP`

__Base image__

CloudOpting provide several base images. Those can be created with crane and are supposed to be stored on the local registry.

__Context__

Environment with a common set of puppet modules which are described in a _puppetfile_.

Images are associated to a context.

A context can have a _group identifier_. This is a custom id to set as image repo. (will see this later)

__Image__

An image is the result of executing a _Dockerfile_ and maybe apply a _puppet manifest_.

There are several ways to build that from:

- Dockerfile + puppet manifest
- base image name + puppet manifest
- Dockerfile

__Puppetfile__

File that list all the puppet modules needed and where to get them.

Take a look at the [official reference](https://docs.puppetlabs.com/pe/latest/r10k_puppetfile.html) or see the example.

Don't forget to install also the dependencies (you can see them on the main page of each module. e.g. https://forge.puppetlabs.com/puppetlabs/mysql/dependencies).

__Puppet manifest__

File that describes how the system will be configured.

__Dockerfile__

Docker recipe for a container.

__docker-compose.yml__

Describes a set of containers, the relation between them, the command to run each one, the volumes to mount, and some other configuration parameters.

__cluster__

Resource that wraps one or several machines (do not try to add several because it is not supported for the moment) under a identifier and allows you to deploy on them.

__composition__

Made adding a _docker-compose file_ to a _context_ and linking to a _cluster_.

# Setup you environment

## Clone this repo

Using:

`git clone https://github.com/CloudOpting/cloudopting-crane`

## Start crane

Start crane using the specific compose file prepared for testing pilots, `pilot-dev.yml`:

`docker-compose -f pilot-dev.yml up`


## Enter the UI

Browse to `http://<docker machine ip>:8888`.

You will see several groups: _builder_, _cluster_, _composition_ and _extra_.

![groups](/docs/resources/commander1.png)

Clicking on each group you can expand the list of methods and selecting a method you can use it introducing the parameters and so on. We'll see later the main methods to help in developing applications.

![groups](/docs/resources/commander2.png)


# Example of use

__NOTE 1__: in crane is possible to add base images to the internal private registry and after use just it name and a puppet manifest to build a image (`/builder/images/bases` routes). For this guide, in order to keep things simple, we'll skip that.

__NOTE 2__: all files in this example are available in [`/examples/migration-guide-1`](/examples/migration-guide-1).

## Example description

We are going to build a simple application based on two services: a _redis_ and a _python flask web server_.

The _redis_ container will be built using the [official redis image](https://hub.docker.com/_/redis/).

The _web_ will use [cloudopting/ubuntubase:14.04](https://hub.docker.com/r/cloudopting/ubuntubase) and a manifest.

## Step 1: __build context__

Build a __context__ with the puppet modules that your entire application needs.

`POST /builder/context` with:

- __puppetfile__: a file like [`puppetfile`](/examples/migration-guide-1) with all the modules and dependencies
- __group__ (_optional_): common label to gather several images. This will become the repo name on the private dockerhub. Left it blank to use `default`.

![post context](/docs/resources/commander-post-context.png)

The response will be something like:

```json
{
  "status": "building",
  "images": [],
  "token": "CTJnnfqI",
  "group": "default",
  "description": "Under creation"
}
```

It's important the `token` parameter, save it.

You can check the status with `GET /builder/context/{token}`.

![get context](/docs/resources/commander-get-context.png)

```json
{
  "status": "finished",
  "images": [],
  "token": "CTJnnfqI",
  "group": "default",
  "description": "Build finished without errors"
}
```

Wait until `status` == `finished`.

## Step 2: __build images__

Build an __image__.

It is possible to use one of the following combinations:

- a _base image name_ and a _puppet manifest_. As we said in __NOTE 1__, we are not using that on this guide.

- a _Dockerfile_ and a _puppet manifest_.

- just a _Dockerfile_.

`POST /builder/images` with:

- __contextReference__: the _context token_ from the previous step.
- __imageName__: leave it blank (__NOTE 1__).
- __dockerfile__: the image _Dockerfile_


First for the __redis__ image:
![post image](/docs/resources/commander-post-image.png)

you'll get something like:
```json
{
  "status": "building",
  "description": "Under creation",
  "tag": "default/redis",
  "token": "CTJnnfqI-IMredis",
  "imageName": "redis",
  "context": "CTJnnfqI"
}
```

With that token you can use: `GET /builder/images/CTJnnfqI-IMredis` to retrieve the status.

![get image](/docs/resources/commander-get-image.png)

```json
{
  "status": "finished",
  "description": "Build finished without errors",
  "imageName": "redis",
  "token": "CTJnnfqI-IMredis",
  "tag": "default/redis",
  "context": "CTJnnfqI"
}
```

Wait until `status` == `finished`.

Now, let's do the same for the _web_ image:
![post image](/docs/resources/commander-post-image2.png)

Notice this time we're using a [`Dockerfile`](/examples/migration-guide-1/web/Dockerfile) (from a cloudopting base) and also a [`manifest.pp`](/examples/migration-guide-1/web/Dockerfile). Take a look at both files to see the details.

This should be the response.

```json
{
  "status": "building",
  "description": "Under creation",
  "tag": "default/redis",
  "token": "CTJnnfqI-IMweb",
  "imageName": "web",
  "context": "CTJnnfqI"
}
```

Do `GET /builder/images/CTJnnfqI-IMweb` to retrieve the status.
![post image](/docs/resources/commander-get-image2.png)

```json
{
  "status": "finished",
  "description": "Build finished without errors",
  "imageName": "web",
  "token": "CTJnnfqI-IMweb",
  "tag": "default/web",
  "context": "CTJnnfqI"
}
```

Wait until `status` == `finished`.


## Step 3: __fake a cluster__

In crane _cluster_ is a generic entity which represents any place where to deploy containers.

For testing, there is a special container with a docker engine inside where you can try to deploy. Crane resolve the name `emulatedhost` to that fake machine.

Create a cluster entity with:

`POST /cluster/provisionedSingleMachine`

- __endpoint__: url where docker engine will be listening. For this example: `http://emulatedhost:4243`
- __apiVersion__: it is possible to force a version, but leave it blank.

![post cluster](/docs/resources/commander-post-cluster.png)

The response should be:

```json
{
  "status": "joining",
  "description": "Ready to use",
  "token": "CLo0BKFI",
  "nodes": [
    {
      "status": "joining",
      "endpoint": "http://emulatedhost:4243"
    }
  ],
  "type": "simple-preprovisioned",
  "numberOfNodes": 1
}
```

Again, we get a _token_. This _cluster token_ can be used as identifier to say crane where to deploy the application (next step).

## Step 4: __deploy__

Now we can use crane to deploy our application on this emulated host.

We need a [`docker-compose.yml` file like this](/examples/migration-guide-1/docker-compose.yml).

Notice images are named like `group/imagename`.

Deploy the app with:

`POST /composer`

- __clusterToken__: the token we obtained in the previous step.
- __composefile__: a valid [`docker-compose.yml`](/examples/migration-guide-1/docker-compose.yml)

![post composition](/docs/resources/commander-post-composition.png)

The application should now being deployed on the host.

For this example the web application listen to the port 5000 which is redirected to the port 80 on the docker host (see the emulatedhost configuration on [pilot-dev.yml](/pilot-dev.yml) )

While testing your application you may need to change that value and maybe add others.

## EXTRA: __debug errors__

You can debug build errors seeing the log and error files.

On the root of this project, go to `application-data/commander/`.

There will be a folder called `builds`, where you will find a folder for each _context_ (named with the _context token_) and inside all the documents related with that. Inside the subfolder `images` there will be a folder for each image, and inside that some logs. The most useful are: `build.log`, `build_err.log`, `pull.log` and `pull_err.log`.
