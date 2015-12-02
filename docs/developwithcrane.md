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

Resource that wraps one or several machines under a identifier and allows you to deploy on them.

__composition__

Made adding a _docker-compose file_ to a _context_ and linking to a _cluster_.

# Setup you environment

## Clone this repo
<!-- TODO -->

## Start crane
<!-- TODO -->

## Enter the UI
<!-- TODO -->

## Logs for debugging
<!-- TODO -->


# Example of use
