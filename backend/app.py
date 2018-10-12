from flask import Flask, request, jsonify
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib
# Run matplotlib in headless mode, prevents NSWindow crash
matplotlib.use('agg')
import matplotlib.pyplot as plt
from Naked.toolshed.shell import execute_js

# declare constants
HOST = '0.0.0.0'
PORT = 8081

# initialize flask application
app = Flask(__name__)


@app.route('/api/orbit', methods=['POST'])
def get_orbit():

    execute_js('orbit.js')

    # Read in dataframe
    try:
        data = pd.read_json('data.json')
        df = data.as_matrix(columns = data.columns[0:2])
    except:
        print('No OrbitDB database found.')

    # Plot original
    plt.figure(1)
    plt.scatter(df[:, 0], df[:, 1]);
    plt.savefig('../frontend/src/assets/images/before.png')
    plt.close()

    return ('', 200)


@app.route('/api/train', methods=['POST'])
def train():

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

    # Plot result
    plt.figure(2)
    plt.scatter(df[:, 0], df[:, 1], c = prediction)
    plt.scatter(centers[:, 0], centers[:, 1], s = 200, alpha = 0.5);
    plt.savefig('../frontend/src/assets/images/after.png')
    plt.close()

    '''
    K-means is not classification, so accuracy doesn't really apply.
    Nevertheless, labels can be loaded for an 'accuracy' metric:
    truth = data['truth'].values
    Compare to the 'prediction' array. Note you may have to use the
    random_state parameter so that cluster ordering is deterministic.
    '''

    return ('', 200)


if __name__ == '__main__':
    # run web server
    app.run(host = HOST,
            debug = True,  # automatic reloading enabled
            port = PORT)
