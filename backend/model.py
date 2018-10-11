'''
The clustering model on its own.
'''

from flask import Flask, request, jsonify
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_json('data.json')
df = data.as_matrix(columns=data.columns[0:2])

# Plot original
plt.figure(1)
plt.scatter(df[:, 0], df[:, 1]);

# K-means cluster
kmeans = KMeans(n_clusters = 4)
kmeans.fit(df)
prediction = kmeans.predict(df)
centers = kmeans.cluster_centers_

# Plot result
plt.figure(2)
plt.scatter(df[:, 0], df[:, 1], c = prediction)
plt.scatter(centers[:, 0], centers[:, 1], s = 200, alpha = 0.5);

# Show both before and after plots
plt.show()

'''
K-means is not classification, so accuracy doesn't really apply.
Nevertheless, labels can be loaded for an 'accuracy' metric:
truth = data['truth'].values
Compare to the 'prediction' array. Note you may have to use the
random_state parameter so that cluster ordering is deterministic.
'''
