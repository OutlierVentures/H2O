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

# For getting Ocean Protocol contract addresses from sibling container
RUN curl -fsSL https://get.docker.com -o get-docker.sh \
    && sh get-docker.sh \
    && rm get-docker.sh

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

RUN cd backend \
    && pip3 install -r requirements.txt

RUN cd backend \
    && npm install orbit-db ipfs

RUN cd frontend \
    && yarn install --pure-lockfile


# Ports

# Ocean
#EXPOSE 8545
#EXPOSE 5000

# Backend
EXPOSE 8081

# Frontend
EXPOSE 4200


# Start H2O

RUN chmod +x docker_start_h2o

CMD ./docker_start_h2o
