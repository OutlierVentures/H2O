#!/bin/bash -x
#AQUARIUSDIR=.
CONF_TEMPLATE=config.ini
CONF_FILE=config_local.ini
#KEEPERDIR=~/Projects/keeper-contracts
#cd $KEEPERDIR
cp $CONF_TEMPLATE $CONF_FILE

# get the docker container ID from the list or running containers
KEEPER_CONTRACTS_DOCKER_ID=`docker container ls | grep keeper-contracts | awk '{print $1}'`

market=$(docker exec -it $KEEPER_CONTRACTS_DOCKER_ID python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanMarket.development.json', 'r'))['address'])")
token=$(docker exec -it $KEEPER_CONTRACTS_DOCKER_ID python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanToken.development.json', 'r'))['address'])")
auth=$(docker exec -it $KEEPER_CONTRACTS_DOCKER_ID python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/OceanAuth.development.json', 'r'))['address'])")
didregistry=$(docker exec -it $KEEPER_CONTRACTS_DOCKER_ID python -c "import sys, json; print(json.load(open('/keeper-contracts/artifacts/DIDRegistry.development.json', 'r'))['address'])")

#result=$(docker exec -it docker_keeper-contracts_1 truffle migrate --reset | grep -P 'OceanMarket:|OceanToken:|OceanAuth:')
#values=$(echo $result | sed 's/OceanToken: /token.address=/' | sed 's/OceanMarket: /\nmarket.address=/' | sed 's/OceanAuth: /\nauth.address=/')
#token=$(echo $values | cut -d' ' -f1)
#market=$(echo $values | cut -d' ' -f2)
#auth=$(echo $values | cut -d' ' -f3)
#cp -R $KEEPERDIR/build/contracts $AQUARIUSDIR/venv/contracts
sed -i -e "/token.address =/c token.address = ${token}" $CONF_FILE
sed -i -e "/market.address =/c market.address = ${market}" $CONF_FILE
sed -i -e "/auth.address =/c auth.address = ${auth}" $CONF_FILE
sed -i -e "/didregistry.address =/c didregistry.address = ${didregistry}" $CONF_FILE

#sed -i -e "/aquarius.address =/c aquarius.address=" $CONF_FILE
