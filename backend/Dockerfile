FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -yq --no-install-recommends \
    python3 \
    python3-pip \
    nodejs \
    npm
RUN pip3 install --upgrade pip==9.0.3 \
    && pip3 install setuptools

# for flask web server
EXPOSE 8081

# set working directory
ADD . /app
WORKDIR /app

# install required libraries
RUN pip3 install pandas matplotlib flask scikit-learn[alldeps]
RUN npm install

# This is the runtime command for the container
CMD python3 app.py
