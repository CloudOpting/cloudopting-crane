# CloudOpting-Crane

## Introduction

Crane is a tool that assist the creation and deploy of docker containers.

It uses several docker components (compose libraries, docker-py, engine, registry) and other pieces of technology (like Puppet) to make a friendly environment where make container microservices applications is easy.

## Process

First it is necessary to introduce several concepts:

- __Base image__: docker image which can be use to build other images on top of it. You can create base images and use them after just referring its name when building an application image.

- __Context__: The environment where some images are builded. For the moment it is formed by the puppet modules which will be available for the builder controller to build images in that context.

- __Image__: Docker template of a service. Can be instantiated in a container.

- __Composition__: Set of containers that forms a complete service.

## General overview

Crane is made with docker. It is composed by several containers:
- __commander__: main piece of this project. Contains the logic to orchestrate all the other components
- __redis__: redis storage used by commander to save several context information
- __engine__: docker engine used for building images
- __registry__: private docker registry

### Commander

Commander is structured as follows.

![Commander](/docs/resources/crane.png)

It serves a REST API (the box with _Flask web microframework_). This API calls internally several controllers depending the requested action. These controllers uses several tools from the toolbox.

## Troubleshooting

### It starts the first time but after that it crashes.

This kind of problems are usually related to a previous forced exit. 
