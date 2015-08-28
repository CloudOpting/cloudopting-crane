FROM ubuntu:14.04

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq

# Copy app
COPY app /usr/src/commander/

# Install git
RUN apt-get install -y git

# Install requirements
RUN apt-get install -y python-pip
RUN pip install -r /usr/src/commander/requirements.txt

# Install puppet and r10k
RUN apt-get install -y puppet
RUN apt-get install -y ruby
RUN gem install r10k

# Add engine certificates
COPY ./certs/client-cert.pem /usr/src/commander/certs/client-cert.pem
COPY ./certs/client-key.pem /usr/src/commander/certs/client-key.pem
COPY ./certs/ca.pem /usr/src/commander/certs/ca.pem

# Add registry certificate
COPY ./certs/registry-ca.crt /usr/src/commander/certs/registry-ca.crt

# Cleaning
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/commander
CMD python commander.py
