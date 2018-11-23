# Ocean Protocol (Outlier Ventures' abstraction)
import register as reg

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
        df = data.values[:, [0, 1]]
        
        # Plot original
        plt.figure(1)
        plt.scatter(df[:, 0], df[:, 1])
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
        df = data.values[:, [0, 1]]
    except:
        print('No OrbitDB database found.')

    # K-means cluster
    kmeans = KMeans(n_clusters = int(parameters['clusters']))
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
    plt.scatter(centers[:, 0], centers[:, 1], s = 200, alpha = 0.5)
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

    '''
    # Uncomment this for OrbitDB hosting (PoC, not Ocean testnet compatible yet)
    execute_js('host.js')
    with open('host.json', 'r') as infile:
        host = json.load(infile)
    '''


    # Azure storage hosting
    azure_account = parameters['azureaccount']

    # Unique container name - requires non-collision * under a single Azure account *
    # 36^4=1679616 possibilities, Pr[collision] = 1 - ( (36^4-1)/36^4 )^num_datasets_created
    container_name = parameters['containername']

    # Generate machine-readable download link to hosted dataset
    azure_url = 'https://' + azure_account + '.blob.core.windows.net/' + container_name + '/output.json'

    try:
        # Create service used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name = azure_account, account_key = parameters['azurekey'])

        # Create container with name = asset_id
        block_blob_service.create_container(container_name)

        # Make public
        block_blob_service.set_container_acl(container_name, public_access = PublicAccess.Container)

        # Create and upload blob
        block_blob_service.create_blob_from_path(container_name, 'output.json', 'output.json')

    except Exception as e:
        print(e)


    # Outlier Ventures' abstraction for easy registration with Keeper and Aquarius
    reg.simple_register(parameters['name'],
                        parameters['price'],
                        parameters['description'],
                        parameters['author'],
                        azure_url)


    return ('', 200)


if __name__ == '__main__':

    # Run web server
    app.run(host = HOST,
            debug = False,  # Enable for auto-reload. Not for production.
            port = PORT)
