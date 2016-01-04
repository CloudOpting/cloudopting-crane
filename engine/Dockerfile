FROM centos:7

# Install docker
RUN yum -y update
ADD docker.repo /etc/yum.repos.d/docker.repo
RUN yum -y install docker-engine
COPY launch.sh /root/launch.sh
RUN chmod +x /root/launch.sh

VOLUME /var/lib/docker

WORKDIR /root
CMD ./launch.sh
