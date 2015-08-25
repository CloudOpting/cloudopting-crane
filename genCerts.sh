#!/bin/bash

# Definitions
export CA_PASSWORD=p4ssw0rd
export ENGINE_HOSTNAME=coengine
export CLIENT_HOSTNAME=commander

# Colors
ERR='\033[0;31m'
INFO='\033[1;36m'
SUCC='\033[0;36m'
ELEM='\033[1;34m'
NC='\033[0m' # No Color

# Gen engine certificates
## CA [ca.pem, ca-key.pem]
printf "${INFO}Generating CA key and cert...${NC}\n\n"
openssl genrsa -aes256 -passout env:CA_PASSWORD -out engine/certs/ca-key.pem 4096
openssl req -new -x509 -passin env:CA_PASSWORD -days 365 -key engine/certs/ca-key.pem \
  -sha256 -out engine/certs/ca.pem -subj "/C=ES/ST=Seville/L=Seville/O=CloudOpting/OU=IT/CN=$ENGINE_HOSTNAME"
printf "\n${SUCC}Got ${ELEM}ca-key.pem${SUCC} and ${ELEM}ca.pem${SUCC} .${NC}\n\n\n"


## Signed server key [server-cert.pem, server-key.pem]
printf "${INFO}Generating server keys...${NC}\n\n"
openssl genrsa -out engine/certs/server-key.pem 4096
openssl req -subj "/CN=$ENGINE_HOSTNAME" -sha256 -new -key engine/certs/server-key.pem -out engine/certs/server.csr
echo subjectAltName = IP:127.0.0.1 > engine/certs/extfile.cnf
openssl x509 -req -days 365 -sha256 -in engine/certs/server.csr -CA engine/certs/ca.pem -CAkey engine/certs/ca-key.pem \
  -CAcreateserial -out engine/certs/server-cert.pem -extfile engine/certs/extfile.cnf -passin env:CA_PASSWORD
rm engine/certs/extfile.cnf
rm -v engine/certs/server.csr
printf "\n${SUCC}Got ${ELEM}server-cert.pem${SUCC} and ${ELEM}server-key.pem${SUCC} .${NC}\n\n\n"



## Signed client key [client-cert.pem, client-key.pem]
printf "${INFO}Generating client keys...${NC}\n\n"
openssl genrsa -out engine/certs/client-key.pem 4096
openssl req -subj "/CN=$CLIENT_HOSTNAME" -new -key engine/certs/client-key.pem -out engine/certs/client.csr
echo extendedKeyUsage = clientAuth > engine/certs/extfile.cnf
openssl x509 -req -days 365 -sha256 -in engine/certs/client.csr -CA engine/certs/ca.pem -CAkey engine/certs/ca-key.pem \
  -CAcreateserial -out engine/certs/client-cert.pem -extfile engine/certs/extfile.cnf -passin env:CA_PASSWORD
rm engine/certs/extfile.cnf
rm -v engine/certs/client.csr
printf "\n${SUCC}Got ${ELEM}client-cert.pem${SUCC} and ${ELEM}client-key.pem${SUCC} .${NC}\n\n\n"



# Set engine cetificates

# Gen registry certificates
# Set registry certificates
