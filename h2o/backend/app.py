# Ocean Protocol
from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

# OrbitDB
from Naked.toolshed.shell import execute_js

# Azure Storage
import uuid, sys
from azure.storage.blob import BlockBlobService, PublicAccess

# Flask
from flask import Flask, request, jsonify

# Utilities
import os, shutil, json, requests, logging, random, string

# Clustering
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib
# Run matplotlib in headless mode, prevents NSWindow crash
matplotlib.use('agg')
import matplotlib.pyplot as plt


# declare constants
HOST = '0.0.0.0'
PORT = 8081

# initialize flask application
app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@app.route('/api/orbit', methods=['POST'])
def get_orbit():

    # OrbitDB writeflag issue workaround: delete local copy on query
    if os.path.exists('orbitdb'):
        shutil.rmtree('orbitdb')

    if os.path.exists('data.json'):
        os.remove('data.json')

    # Get parameters for OrbitDB
    parameters = request.get_json()

    # Write OrbitDB address to file
    output = {
        "address": parameters['address']
    }
    with open('config.json', 'w') as outfile:
        json.dump(output, outfile)

    execute_js('orbit.js')

    # Read in dataframe
    try:
        data = pd.read_json('data.json')
        df = data.as_matrix(columns = data.columns[0:2])

        # Plot original
        plt.figure(1)
        plt.scatter(df[:, 0], df[:, 1]);
        plt.savefig('../frontend/src/assets/images/before.png')
        plt.close()

    except:
        print('No OrbitDB database found.')

    return ('', 200)


@app.route('/api/train', methods=['POST'])
def train():

    # OrbitDB writeflag issue workaround: delete local copy on query
    if os.path.exists('orbitdb'):
        shutil.rmtree('orbitdb')

    if os.path.exists('output.json'):
        os.remove('output.json')

    # Get parameters for clustering
    parameters = request.get_json()

    # Read in dataframe
    try:
        data = pd.read_json('data.json')
        df = data.as_matrix(columns = data.columns[0:2])
    except:
        print('No OrbitDB database found.')

    # K-means cluster
    kmeans = KMeans(n_clusters = int(parameters['C']))
    kmeans.fit(df)
    prediction = kmeans.predict(df)
    centers = kmeans.cluster_centers_

    # Write clustered output to file
    output = {
        "data": df.tolist(),
        "cluster": prediction.tolist(),
        "centroids": centers.tolist()
    }
    with open('output.json', 'w') as outfile:
        json.dump(output, outfile)

    # Plot result
    plt.figure(2)
    plt.scatter(df[:, 0], df[:, 1], c = prediction)
    plt.scatter(centers[:, 0], centers[:, 1], s = 200, alpha = 0.5);
    plt.savefig('../frontend/src/assets/images/after.png')
    plt.close()

    '''
    K-means is not classification, so accuracy doesn't really apply.
    Nevertheless, labels can be loaded for an 'accuracy' metric:
    truth = data['t'].values
    Compare to the 'prediction' array. Note you may have to use the
    random_state parameter so that cluster ordering is deterministic.
    '''

    return ('', 200)


@app.route('/api/ocean', methods=['POST'])
def publish_asset():

    # Get parameters for clustering
    parameters = request.get_json()


    """
    Web3 runs on the host.
    The host OS check is necessary for a containerised launch.
    For developers: if you see a 'too many requests' error,
    you need to change web3_host. This may be 172.17.0.1 on some systems.
    """
    host_os = os.environ.get('HOST_OS')
    if host_os == 'linux':
        web3_host = 'http://172.19.0.1'
    elif host_os == 'macos':
        web3_host = 'http://docker.for.mac.host.internal'
    else:
        web3_host = 'http://0.0.0.0'


    azure_account = parameters['azureaccount']

    # Unique asset ID: 40 lowercase alphabetic characters (Azure compatible)
    # Cannot take sample larger than population (26), so take two and combine
    sample_one = ''.join(random.sample(string.ascii_lowercase, 20))
    sample_two = ''.join(random.sample(string.ascii_lowercase, 20))
    asset_id = sample_one + sample_two

    # Uncomment this and comment out Azure try-except block for OrbitDB hosting.
    # OrbitDB hosting is proof-of-concept and not testnet compatible yet.
    #execute_js('host.js')
    #with open('host.json', 'r') as infile:
    #    host = json.load(infile)

    # Azure storage hosting
    try:
        # Create service used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name = azure_account, account_key = parameters['azurekey'])

        # Create container with name = asset_id
        container_name = asset_id
        block_blob_service.create_container(asset_id)

        # Make public
        block_blob_service.set_container_acl(asset_id, public_access = PublicAccess.Container)

        # Create and upload blob
        block_blob_service.create_blob_from_path(asset_id, 'output.json', 'output.json')

    except Exception as e:
        print(e)


    ocean = OceanContracts(host = web3_host,
                           port = 8545,
                           config_path = './config_local.ini')

    json_consume = {
        "metadata": {
            # User-specified
            "name": parameters['name'],
            "description": parameters['description'],
            # ContentUrls is a list. Use commented line for OrbitDB hosting (not testnet compatible yet)
            "contentUrls": ['https://' + azure_account + '.blob.core.windows/net/' + asset_id + '/output.json'],
            #"contentUrls": [host['address'],'https://ipfs.io/ipfs/QmeESXh9wPib8Xz7hdRzHuYLDuEUgkYTSuujZ2phQfvznQ/#dbaddress'],
            "price": parameters['price'],
            "author": parameters['author'],
            # Fixed
            "type": "dataset",
            "licence": "CC-BY",
            # Internal, used to generate resource ID
            "links": "",
            "size": "",
            "format": ""
        },
        ## Generate unique assetID (40-byte hex)
        "assetId": asset_id
    }

    resource_id = register(publisher_account = ocean.web3.eth.accounts[1],
                           provider_account = ocean.web3.eth.accounts[0],
                           price = parameters['price'],
                           ocean_contracts_wrapper = ocean,
                           json_metadata = json_consume,
                           provider_host = web3_host + ':5000')

    assert requests.get(web3_host + ':5000/api/v1/provider/assets/metadata/%s' % resource_id).status_code == 200

    return ('', 200)


if __name__ == '__main__':

    # Run web server
    app.run(host = HOST,
            debug = True,  # Automatic reloading enabled
            port = PORT)
