#!/bin/bash

# Definitions
export CA_PASSWORD=p4ssw0rd
export ENGINE_HOSTNAME=coengine
export CLIENT_HOSTNAME=commander
export ENGINE_BASE_DIR=engine/certs


# Colors
ERR='\033[0;31m'
INFO='\033[1;36m'
BINFO='\033[1;33m'
SUCC='\033[0;36m'
UINFO='\033[0;37m'
ELEM='\033[1;34m'
NC='\033[0m' # No Color

# Gen engine certificates
mkdir -p ${ENGINE_BASE_DIR}
## CA [ca.pem, ca-key.pem]
printf "${INFO}Generating CA key and cert...${NC}\n\n"
openssl genrsa -aes256 -passout env:CA_PASSWORD -out ${ENGINE_BASE_DIR}/ca-key.pem 4096
openssl req -new -x509 -passin env:CA_PASSWORD -days 365 -key ${ENGINE_BASE_DIR}/ca-key.pem \
  -sha256 -out ${ENGINE_BASE_DIR}/ca.pem -subj "/C=ES/ST=Seville/L=Seville/O=CloudOpting/OU=IT/CN=$ENGINE_HOSTNAME"
printf "\n${SUCC}Got ${ELEM}ca-key.pem${SUCC} and ${ELEM}ca.pem${SUCC} .${NC}\n\n\n"


## Signed server key [server-cert.pem, server-key.pem]
printf "${INFO}Generating server keys...${NC}\n\n"
openssl genrsa -out ${ENGINE_BASE_DIR}/server-key.pem 4096
openssl req -subj "/CN=$ENGINE_HOSTNAME" -sha256 -new -key ${ENGINE_BASE_DIR}/server-key.pem -out ${ENGINE_BASE_DIR}/server.csr
echo subjectAltName = IP:127.0.0.1 > ${ENGINE_BASE_DIR}/extfile.cnf
openssl x509 -req -days 365 -sha256 -in ${ENGINE_BASE_DIR}/server.csr -CA ${ENGINE_BASE_DIR}/ca.pem -CAkey ${ENGINE_BASE_DIR}/ca-key.pem \
  -CAcreateserial -out ${ENGINE_BASE_DIR}/server-cert.pem -extfile ${ENGINE_BASE_DIR}/extfile.cnf -passin env:CA_PASSWORD
rm ${ENGINE_BASE_DIR}/extfile.cnf
rm -v ${ENGINE_BASE_DIR}/server.csr
printf "\n${SUCC}Got ${ELEM}server-cert.pem${SUCC} and ${ELEM}server-key.pem${SUCC} .${NC}\n\n\n"



## Signed client key [client-cert.pem, client-key.pem]
printf "${INFO}Generating client keys...${NC}\n\n"
openssl genrsa -out ${ENGINE_BASE_DIR}/client-key.pem 4096
openssl req -subj "/CN=$CLIENT_HOSTNAME" -new -key ${ENGINE_BASE_DIR}/client-key.pem -out ${ENGINE_BASE_DIR}/client.csr
echo extendedKeyUsage = clientAuth > ${ENGINE_BASE_DIR}/extfile.cnf
openssl x509 -req -days 365 -sha256 -in ${ENGINE_BASE_DIR}/client.csr -CA ${ENGINE_BASE_DIR}/ca.pem -CAkey ${ENGINE_BASE_DIR}/ca-key.pem \
  -CAcreateserial -out ${ENGINE_BASE_DIR}/client-cert.pem -extfile ${ENGINE_BASE_DIR}/extfile.cnf -passin env:CA_PASSWORD
rm ${ENGINE_BASE_DIR}/extfile.cnf
rm -v ${ENGINE_BASE_DIR}/client.csr
printf "\n${SUCC}Got ${ELEM}client-cert.pem${SUCC} and ${ELEM}client-key.pem${SUCC} .${NC}\n\n\n"

## How to set client certificates
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"
printf "${BINFO}  These notes help you to configure manually the docker engine and docker client with the generated certificates.${NC}\n"
printf         "  If your plan is to use the elements in this project (${ELEM}engine${BINFO} and ${ELEM}commander${BINFO}), you can ignore them.${NC}\n"
printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n"


printf "\n${BINFO}BONUS:${INFO} How to set client certificates:${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/client-cert.pem${UINFO} to ${ELEM}~/.docker/cert.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/client-key.pem${UINFO} to ${ELEM}~/.docker/key.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/ca.pem${UINFO} to ${ELEM}~/.docker/ca.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Set permissions ${ELEM}0600${UINFO} to the previous files.${NC}\n\n"
printf "  ${INFO}The client must be able to resolve the name (which is configured in this script as ${ELEM}ENGINE_HOSTNAME=${ENGINE_HOSTNAME}${NC}) of the docker engine.${NC}\n"

printf "\n${BINFO}BONUS II:${INFO} How to configure environment to allow docker client communicate with docker engine:${NC}\n"
printf "\t${UINFO}Set the following environment variables in the client machine:\n"
printf "\t\t${UINFO}· DOCKER_TLS_VERIFY=1\n"
printf "\t\t${UINFO}· DOCKER_CERT_PATH=/home/user/.docker\n"
printf "\t\t${UINFO}· DOCKER_HOST=tcp://${ENGINE_HOSTNAME}:4243\n"
printf "\t\t${UINFO}Assuming 4243 is the port where the docker daemon will be listening, ${ELEM}user${UINFO} is the user who execute docker client\n"
printf "\t\tand you can resolve ${ELEM}${ENGINE_HOSTNAME}${UINFO} to the address where the engine is running.${NC}\n"

printf "\n${BINFO}BONUS III:${INFO} How to configure certificates in engine:${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/server-cert.pem${UINFO} to ${ELEM}/root/.docker/cert.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/server-key.pem${UINFO} to ${ELEM}/root/.docker/key.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Copy ${ELEM}${ENGINE_BASE_DIR}/ca.pem${UINFO} to ${ELEM}/root/.docker/ca.pem${UINFO}.${NC}\n"
printf "\t${UINFO}- Add the following options to ${ELEM}DOCKER_OPTS${UINFO} (the location of ${ELEM}DOCKER_OPTS${UINFO} depends on the linux distribution):\n"
printf "\t\t${ELEM} --tlsverify --tlscacert=/root/.docker/ca.pem --tlscert=/root/.docker/cert.pem --tlskey=/root/.docker/key.pem${NC}\n"

printf "${BINFO}-----------------------------------------------------------------------------------------------------------------------${NC}\n\n"



# Set engine cetificates

# Gen registry certificates
# Set registry certificates
