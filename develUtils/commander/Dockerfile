FROM centos:7
# Update repos and isntall enterprise linux repository
RUN yum -y update && yum -y install epel-release
# Install pip
RUN yum -y install python-pip
# Install commander dependencies
ADD ./requirements.txt /usr/src/commander/
RUN pip install -r /usr/src/commander/requirements.txt
# Install ruby
RUN yum -y install gem
# Install r10k
RUN yum -y install r10k
