# Troubleshooting

## 1) Cannot start because cannot link to registry container

This is usually related with the problem of not having the certificates on the proper folder (or not having certificates at all).

Use first the `/genCerts.sh` script to generate the certificates locally.

## 2) It starts the first time but after that it crashes.
or
## 3) Errors like: `Could not find container for entity id...`

This kind of problems are usually related to a previous forced exit.
Remove the containers (`docker rm -f -v $(docker ps -a -q)`) and instance them again.

Is there a new problem related with linking contianers? Don't know why but sometimes docker don't update the local database where it stores the linking information. Fortunately we can regenerate that by removing it. Do this:

`rm -rf /var/lib/docker/containers/*`

`rm -rf /var/lib/docker/volumes/*`

`rm -rf /var/lib/docker/linkgraph.db`

Restart the docker service.

Still not working? Depending on how the previous instance exited, it could be something wrong on the system. Do the previous steps and reboot the system.

## Errors executing _engine_ or _emulatedhost_

If you are using a version previous to _1.0-beta.1_, remove the images and upgrade to this version.

If you are on this version or superior, try the solution for __3)__.

## Error starting tests

Make sure you have the certificates (__1)__), remove the containers, and try again.

If the tests fails, please report the error attaching the output of:

`docker logs testrunner`.
