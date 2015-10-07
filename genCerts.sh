#!/bin/bash

# Definitions
export ENGINE_HOSTNAME=coengine
export CLIENT_HOSTNAME=commander
export EMULATEDHOST_HOSTNAME=emulatedhost
export CA_PASSWORD=p4ssw0rd
export ENGINE_CERTS_DIR=engine/certs
export COMMANDER_CERTS_DIR=commander/certs
export COMMANDER_MASTER_CERTS_DIR=commander/certs/master
export TESTRUNNER_CERTS_DIR=tests/testrunner/certs
export EMULATEDHOST_CERTS_DIR=tests/emulatedhost/certs

export REGISTRY_HOSTNAME=coregistry
export REGISTRY_AUTH_DIR=registry/auth
export REGISTRY_CERTS_DIR=registry/certs
export REGISTRY_DEF_USER=reguser
export REGISTRY_DEF_USER_PASS=s3cr3tp4ssw0rd


# Colors
ERR='\033[0;31m'
INFO='\033[1;36m'
BINFO='\033[1;33m'
SUCC='\033[0;36m'
UINFO='\033[0;37m'
ELEM='\033[1;34m'
OP='\033[2;33m'
NC='\033[0m' # No Color

# Clean previous certs
rm -rf ${ENGINE_CERTS_DIR} ${REGISTRY_AUTH_DIR} ${REGISTRY_CERTS_DIR} ${COMMANDER_CERTS_DIR} ${COMMANDER_MASTER_CERTS_DIR} ${COMMANDER_CERTS_DIR} ${TESTRUNNER_CERTS_DIR} ${EMULATEDHOST_CERTS_DIR}


# ENGINE CERTIFICATES
mkdir -p ${ENGINE_CERTS_DIR}
## CA [ca.pem, ca-key.pem]
printf "${INFO}Generating CA key and cert...${NC}\n\n"
printf "${OP}"
openssl genrsa -aes256 -passout env:CA_PASSWORD -out ${ENGINE_CERTS_DIR}/ca-key.pem 4096
openssl req -new -x509 -passin env:CA_PASSWORD -days 365 -key ${ENGINE_CERTS_DIR}/ca-key.pem \
  -sha256 -out ${ENGINE_CERTS_DIR}/ca.pem -subj "/C=ES/ST=Seville/L=Seville/O=CloudOpting/OU=IT/CN=$ENGINE_HOSTNAME"
printf "${NC}"
printf "\n${SUCC}Got ${ELEM}ca-key.pem${SUCC} and ${ELEM}ca.pem${SUCC} .${NC}\n\n\n"


## Signed server key [server-cert.pem, server-key.pem]
printf "${INFO}Generating server keys...${NC}\n\n"
printf "${OP}"
openssl genrsa -out ${ENGINE_CERTS_DIR}/server-key.pem 4096
openssl req -subj "/CN=$ENGINE_HOSTNAME" -sha256 -new -key ${ENGINE_CERTS_DIR}/server-key.pem -out ${ENGINE_CERTS_DIR}/server.csr
echo subjectAltName = IP:127.0.0.1 > ${ENGINE_CERTS_DIR}/extfile.cnf
openssl x509 -req -days 365 -sha256 -in ${ENGINE_CERTS_DIR}/server.csr -CA ${ENGINE_CERTS_DIR}/ca.pem -CAkey ${ENGINE_CERTS_DIR}/ca-key.pem \
  -CAcreateserial -out ${ENGINE_CERTS_DIR}/server-cert.pem -extfile ${ENGINE_CERTS_DIR}/extfile.cnf -passin env:CA_PASSWORD
rm ${ENGINE_CERTS_DIR}/extfile.cnf
rm -v ${ENGINE_CERTS_DIR}/server.csr
printf "${NC}"
printf "\n${SUCC}Got ${ELEM}server-cert.pem${SUCC} and ${ELEM}server-key.pem${SUCC} .${NC}\n\n\n"



## Signed client key [client-cert.pem, client-key.pem]
printf "${INFO}Generating client keys...${NC}\n\n"
printf "${OP}"
openssl genrsa -out ${ENGINE_CERTS_DIR}/client-key.pem 4096
openssl req -subj "/CN=$CLIENT_HOSTNAME" -new -key ${ENGINE_CERTS_DIR}/client-key.pem -out ${ENGINE_CERTS_DIR}/client.csr
echo extendedKeyUsage = clientAuth > ${ENGINE_CERTS_DIR}/extfile.cnf
openssl x509 -req -days 365 -sha256 -in ${ENGINE_CERTS_DIR}/client.csr -CA ${ENGINE_CERTS_DIR}/ca.pem -CAkey ${ENGINE_CERTS_DIR}/ca-key.pem \
  -CAcreateserial -out ${ENGINE_CERTS_DIR}/client-cert.pem -extfile ${ENGINE_CERTS_DIR}/extfile.cnf -passin env:CA_PASSWORD
rm ${ENGINE_CERTS_DIR}/extfile.cnf
rm -v ${ENGINE_CERTS_DIR}/client.csr
printf "${NC}"
printf "\n${SUCC}Got ${ELEM}client-cert.pem${SUCC} and ${ELEM}client-key.pem${SUCC} .${NC}\n\n\n"

## Copying client certificates to commander context.
mkdir -p ${COMMANDER_CERTS_DIR}
printf "${INFO}Copying client certificates to commander context...${NC}\n\n"
printf "${OP}"
cp ${ENGINE_CERTS_DIR}/client-cert.pem ${COMMANDER_CERTS_DIR}/cert.pem
cp ${ENGINE_CERTS_DIR}/client-key.pem ${COMMANDER_CERTS_DIR}/key.pem
cp ${ENGINE_CERTS_DIR}/ca.pem ${COMMANDER_CERTS_DIR}/ca.pem
printf "${NC}"
printf "\n${SUCC}Copied ${ELEM}(client-)cert.pem${SUCC}, ${ELEM}(client-)key.pem${SUCC} and ${ELEM}ca.pem${SUCC} to ${ELEM}${COMMANDER_CERTS_DIR}${SUCC}.${NC}\n\n\n"

## Copying master client certificates to commander context.
mkdir -p ${COMMANDER_CERTS_DIR}
mkdir -p ${COMMANDER_MASTER_CERTS_DIR}
printf "${INFO}Copying master client certificates to commander context...${NC}\n\n"
printf "${OP}"
cp ${ENGINE_CERTS_DIR}/client-cert.pem ${COMMANDER_MASTER_CERTS_DIR}/cert.pem
cp ${ENGINE_CERTS_DIR}/client-key.pem ${COMMANDER_MASTER_CERTS_DIR}/key.pem
cp ${ENGINE_CERTS_DIR}/ca.pem ${COMMANDER_MASTER_CERTS_DIR}/ca.pem
printf "${NC}"
printf "\n${SUCC}Copied ${ELEM}(client-)cert.pem${SUCC}, ${ELEM}(client-)key.pem${SUCC} and ${ELEM}ca.pem${SUCC} to ${ELEM}${COMMANDER_MASTER_CERTS_DIR}${SUCC}.${NC}\n\n\n"

## How to set client certificates
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"
printf "${BINFO}  These notes help you to configure manually the docker engine and docker client with the generated certificates.${NC}\n"
printf "${BINFO}  If your plan is to use the elements in this project (${ELEM}engine${BINFO} and ${ELEM}commander${BINFO}), you can ignore them.${NC}\n"
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"

printf "\n${BINFO}NOTE I:${INFO} How to set client certificates:${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/client-cert.pem${UINFO} to ${ELEM}~/.docker/cert.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/client-key.pem${UINFO} to ${ELEM}~/.docker/key.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/ca.pem${UINFO} to ${ELEM}~/.docker/ca.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Set permissions ${ELEM}0600${UINFO} to the previous files.${NC}\n\n"
printf "  ${INFO}The client must be able to resolve the name (which is configured in this script as ${ELEM}ENGINE_HOSTNAME=${ENGINE_HOSTNAME}${NC}) of the docker engine.${NC}\n"

printf "\n${BINFO}NOTE II:${INFO} How to configure environment to allow docker client communicate with docker engine:${NC}\n"
printf "\t${UINFO}Set the following environment variables in the client machine:\n"
printf "\t\t${UINFO}· DOCKER_TLS_VERIFY=1\n"
printf "\t\t${UINFO}· DOCKER_CERT_PATH=/home/user/.docker\n"
printf "\t\t${UINFO}· DOCKER_HOST=tcp://${ENGINE_HOSTNAME}:4243\n"
printf "\t\t${UINFO}Assuming 4243 is the port where the docker daemon will be listening, ${ELEM}user${UINFO} is the user who execute docker client\n"
printf "\t\tand you can resolve ${ELEM}${ENGINE_HOSTNAME}${UINFO} to the address where the engine is running.${NC}\n"

printf "\n${BINFO}NOTE III:${INFO} How to configure certificates in engine:${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/server-cert.pem${UINFO} to ${ELEM}/root/.docker/cert.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/server-key.pem${UINFO} to ${ELEM}/root/.docker/key.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_CERTS_DIR}/ca.pem${UINFO} to ${ELEM}/root/.docker/ca.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Add the following options to ${ELEM}DOCKER_OPTS${UINFO} (the location of ${ELEM}DOCKER_OPTS${UINFO} depends on the linux distribution):\n"
printf "\t\t${ELEM} --tlsverify --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem${NC}\n"

printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n\n"




# REGISTRY CERTIFICATES
mkdir -p ${REGISTRY_AUTH_DIR}
mkdir -p ${REGISTRY_CERTS_DIR}
## Create htpasswd with user for basic autentication
printf "${OP}"
mkdir -p ${REGISTRY_AUTH_DIR}
htpasswd -Bbn ${REGISTRY_DEF_USER} ${REGISTRY_DEF_USER_PASS} > ${REGISTRY_AUTH_DIR}/htpasswd
printf "${NC}"

## Create domain certificates for registry
printf "${OP}"
mkdir -p ${REGISTRY_CERTS_DIR}
openssl req -subj "/CN=$REGISTRY_HOSTNAME" -newkey rsa:4096 -nodes -sha256 -keyout ${REGISTRY_CERTS_DIR}/domain.key -x509 -days 365 -out ${REGISTRY_CERTS_DIR}/domain.crt
printf "${NC}"

## Copy domain certificates to commander
mkdir -p ${COMMANDER_CERTS_DIR}
printf "${INFO}Copying domain certificate to commander context...${NC}\n\n"
printf "${OP}"
cp ${REGISTRY_CERTS_DIR}/domain.crt ${COMMANDER_CERTS_DIR}/registry-ca.crt
printf "${NC}"
printf "\n${SUCC}Copied ${ELEM}domain.crt${SUCC} to ${ELEM}${COMMANDER_CERTS_DIR}/registry-ca.crt${SUCC}.${NC}\n\n\n"


## Copy domain certificates to engine
printf "${INFO}Copying domain certificate to engine context...${NC}\n\n"
printf "${OP}"
cp ${REGISTRY_CERTS_DIR}/domain.crt ${ENGINE_CERTS_DIR}/registry-ca.crt
printf "${NC}"
printf "\n${SUCC}Copied ${ELEM}domain.crt${SUCC} to ${ELEM}${ENGINE_CERTS_DIR}/registry-ca.crt${SUCC}.${NC}\n\n\n"

## How to make docker daemon trust docker registry
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"
printf "${BINFO}  These notes help you to configure manually a docker engine to trust the docker registry that use the generated certs.${NC}\n"
printf "${BINFO}  If your plan is to use the elements in this project (${ELEM}engine${BINFO} and ${ELEM}registry${BINFO}), you can ignore them.${NC}\n"
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"

printf "\n${BINFO}NOTE I:${INFO} Use the generated certificate in a docker registry:${NC}\n"
printf "\t${UINFO}- Copy the certificate and the key to the registry:\n"
printf "\t\t${UINFO}· ${ELEM}${REGISTRY_CERTS_DIR}/domain.crt${UINFO} to ${ELEM}certs/domain.crt${UINFO}.${NC}\n"
printf "\t\t${UINFO}· ${ELEM}${REGISTRY_CERTS_DIR}/domain.key${UINFO} to ${ELEM}certs/domain.key${UINFO}.${NC}\n"
printf "\t${UINFO}- Set the following environment variables in the registry:\n"
printf "\t\t${UINFO}· REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt\n"
printf "\t\t${UINFO}· REGISTRY_HTTP_TLS_KEY=/certs/domain.key\n"
printf "  ${INFO}The client must be able to resolve the name (which is configured in this script as ${ELEM}HOSTNAME_HOSTNAME=${ENGINE_HOSTNAME}${NC}) of the docker engine.${NC}\n"

printf "\n${BINFO}NOTE II:${INFO} Instruct docker engine to trust registry:${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${REGISTRY_CERTS_DIR}/domain.crt${UINFO} to ${ELEM}/etc/docker/certs.d/myregistrydomain.com:5000/ca.crt${UINFO}.${NC}\n"
printf "\t${UINFO}- Restart docker engine.${NC}\n"

printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n\n"

# Test environment

## Copying engine certificates to emulatedhost context.
mkdir -p ${EMULATEDHOST_CERTS_DIR}
cp ${ENGINE_CERTS_DIR}/ca.pem ${EMULATEDHOST_CERTS_DIR}/ca.pem
cp ${ENGINE_CERTS_DIR}/registry-ca.crt ${EMULATEDHOST_CERTS_DIR}/registry-ca.crt

## Signed emulatedhost key [emulatedhost-cert.pem, emulatedhost-key.pem]
printf "${OP}"
openssl genrsa -out ${EMULATEDHOST_CERTS_DIR}/emulatedhost-key.pem 4096
openssl req -subj "/CN=$EMULATEDHOST_HOSTNAME" -sha256 -new -key ${EMULATEDHOST_CERTS_DIR}/emulatedhost-key.pem -out ${EMULATEDHOST_CERTS_DIR}/emulatedhost.csr
echo subjectAltName = IP:127.0.0.1 > ${EMULATEDHOST_CERTS_DIR}/extfile.cnf
openssl x509 -req -days 365 -sha256 -in ${EMULATEDHOST_CERTS_DIR}/emulatedhost.csr -CA ${ENGINE_CERTS_DIR}/ca.pem -CAkey ${ENGINE_CERTS_DIR}/ca-key.pem \
  -CAcreateserial -out ${EMULATEDHOST_CERTS_DIR}/emulatedhost-cert.pem -extfile ${EMULATEDHOST_CERTS_DIR}/extfile.cnf -passin env:CA_PASSWORD
rm ${EMULATEDHOST_CERTS_DIR}/extfile.cnf
rm -v ${EMULATEDHOST_CERTS_DIR}/emulatedhost.csr
printf "${OP}"

## Copy all the certificates in engine to testrunner
cp -r ${COMMANDER_CERTS_DIR} ${TESTRUNNER_CERTS_DIR}
