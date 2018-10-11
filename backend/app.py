from flask import Flask, request, jsonify
from sklearn import svm
from sklearn import datasets
from sklearn.externals import joblib
import pandas as pd
import matplotlib.pyplot as plt

# declare constants
HOST = '0.0.0.0'
PORT = 8081

# initialize flask application
app = Flask(__name__)


@app.route('/api/train', methods=['POST'])
def train():
    # get parameters from request
    parameters = request.get_json()



    data = pd.read_json('data.json')
    df = data.as_matrix(columns = data.columns[0:2])

    # Plot original
    plt.figure(1)
    plt.scatter(df[:, 0], df[:, 1]);
    plt.savefig('../frontend/src/assets/images/before.png')

    # K-means cluster
    kmeans = KMeans(n_clusters = parameters['C'])
    kmeans.fit(df)
    prediction = kmeans.predict(df)
    centers = kmeans.cluster_centers_

    # Plot result
    plt.figure(2)
    plt.scatter(df[:, 0], df[:, 1], c = prediction)
    plt.scatter(centers[:, 0], centers[:, 1], s = 200, alpha = 0.5);
    plt.savefig('../frontend/src/assets/images/after.png')


    '''
    K-means is not classification, so accuracy doesn't really apply.
    Nevertheless, labels can be loaded for an 'accuracy' metric:
    truth = data['truth'].values
    Compare to the 'prediction' array. Note you may have to use the
    random_state parameter so that cluster ordering is deterministic.
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
