# THIS SHOULD BE IN THE h2o FOLDER

FROM ubuntu:18.04


# For package installs

ARG DEBIAN_FRONTEND=noninteractive


# Install required software

# Core tools, python
RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
    git \
    apt-utils \
    curl \
    gnupg \
    build-essential \
    python3-dev \
    python3-pip

# For Ocean Protocol, 1.22 for non-suffixed container names
RUN curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh \
    && curl -L "https://github.com/docker/compose/releases/download/1.22.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose \
    && chmod +x /usr/local/bin/docker-compose

# Node and npm
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash - \
    && apt-get install -yq --no-install-recommends nodejs

# Yarn
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update \
    && apt-get install yarn

# Angular
RUN npm install -g @angular/cli

# Python core tools
RUN pip3 install --upgrade setuptools \
    && pip3 install wheel


# Set up directory
ADD . /app
WORKDIR /app


# Install modules

RUN cd h2o/backend \
    && pip3 install -r requirements.txt

RUN cd h2o/backend \
    && npm install orbit-db ipfs

RUN cd h2o/frontend \
    && yarn install --pure-lockfile


# Ports

# Ocean Protocol
# EXPOSE 5000 8545 9984 9985 46656 46657

# Backend
EXPOSE 8081

# Frontend
EXPOSE 4200


# Start H2O

RUN chmod +x docker_start

CMD ./docker_start
