#!/bin/bash

echo "The main field you must introduce is the CN (Common Name). It must be something like 'registry.cloudopting.dev' and must be resolvable by someone who wants to interact with the registry."
echo "This must generate a folder (named as 'certs') and two files inside (domain.key and 'domain.crt')"
mkdir -p certs && openssl req -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key -x509 -days 365 -out certs/domain.crt
