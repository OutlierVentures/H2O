from flask import Flask, request, jsonify

from sklearn import svm
from sklearn import datasets
from sklearn.externals import joblib

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
    data = pd.read_json('data.json')

    df = data.as_matrix(columns = data.columns[0:2])

    # Plot original
    plt.figure(1)
    plt.scatter(df[:, 0], df[:, 1]);
    plt.savefig('../frontend/src/assets/images/before.png')

    return ('', 200)

@app.route('/api/train', methods=['POST'])
def train():
    # get parameters from request
    parameters = request.get_json()



    '''
    Paste model here.
    Need to import orbitdb database first i.e. RUN node orbit.
    '''


    # read iris data set
    iris = datasets.load_iris()
    X, y = iris.data, iris.target

    # fit model
    clf = svm.SVC(C=float(parameters['C']),
                  probability=True,
                  random_state=1)
    clf.fit(X, y)

    # persist model
    joblib.dump(clf, 'model.pkl')

    return jsonify({'accuracy': round(clf.score(X, y) * 100, 2)})


@app.route('/api/predict', methods=['POST'])
def predict():
    # get iris object from request
    X = request.get_json()
    X = [[float(X['sepalLength']), float(X['sepalWidth']), float(X['petalLength']), float(X['petalWidth'])]]

    # read model
    clf = joblib.load('model.pkl')
    probabilities = clf.predict_proba(X)

    return jsonify([{'name': 'Iris-Setosa', 'value': round(probabilities[0, 0] * 100, 2)},
                    {'name': 'Iris-Versicolour', 'value': round(probabilities[0, 1] * 100, 2)},
                    {'name': 'Iris-Virginica', 'value': round(probabilities[0, 2] * 100, 2)}])


if __name__ == '__main__':
    # run web server
    app.run(host=HOST,
            debug=True,  # automatic reloading enabled
            port=PORT)
