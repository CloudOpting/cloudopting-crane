FROM ubuntu:14.04

RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update -qq

# Install some dependencies
RUN apt-get install -yqq git python-dev libffi-dev libssl-dev

# Install puppet and r10k
RUN apt-get install -yqq puppet
RUN apt-get install -yqq ruby
RUN gem install r10k --quiet

# Copy app
COPY app /usr/src/commander/

# Install requirements
RUN apt-get install -yqq python-pip
RUN pip install -r /usr/src/commander/requirements.txt --force-reinstall --upgrade -I

# Install docker client (required by docker-py)
COPY ./docker-client-exec /usr/bin/docker

# Cleaning
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /usr/src/commander
CMD python commander.py
