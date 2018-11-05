# Ocean Protocol
from squid_py.ocean_contracts import OceanContracts
from squid_py.consumer import register

# OrbitDB
from Naked.toolshed.shell import execute_js

# Flask
from flask import Flask, request, jsonify

# Utilities
import os, shutil, json, requests, binascii, requests, logging

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

    # IS HOST, SO RUNS UNTIL MANUALLY CLOSED
    execute_js('host.js')

    with open('host.json', 'r') as infile:
        host = json.load(infile)

    ocean = OceanContracts(host = 'http://0.0.0.0',
                           port = 8545,
                           config_path = './config_local.ini')

    json_consume = {
        "metadata": {
            # User-specified
            "name": parameters['name'],
            "description": parameters['description'],
            "contentUrls": [host['address'],'https://ipfs.io/ipfs/QmeESXh9wPib8Xz7hdRzHuYLDuEUgkYTSuujZ2phQfvznQ/#dbaddress'], # List
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
        "assetId": binascii.b2a_hex(os.urandom(20))
    }

    resource_id = register(publisher_account = ocean.web3.eth.accounts[1],
                           provider_account = ocean.web3.eth.accounts[0],
                           price = parameters['price'],
                           ocean_contracts_wrapper = ocean,
                           json_metadata = json_consume,
                           provider_host = 'http://0.0.0.0:5000')

    assert requests.get('http://0.0.0.0:5000/api/v1/provider/assets/metadata/%s' % resource_id).status_code == 200

    return ('', 200)


if __name__ == '__main__':

    # run web server
    app.run(host = HOST,
            debug = True,  # automatic reloading enabled
            port = PORT)
