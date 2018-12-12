import numpy as np
from sklearn.cluster import DBSCAN


def get_dbscan_prediction_min(data):
    """ Function that clusters data from TrackStream objects

    :param data: The data to cluster using the dbscan algorithm
    :return: a tuple, in which there is :
        - in first position the array of predictions for all tracks given in entry
        - in second position an array containing the IDs of the predicted tracks.
    """
    np_data = np.array(data)
    prediction = DBSCAN(min_samples=1).fit_predict(np_data[:, 1:3])
    return prediction, np_data[:, -1]


def get_dbscan_prediction(data, all_tracks_data={}):
    """ Function that clusters data from TrackStream objects

    :param data: The data to cluster using the dbscan algorithm
    :param all_tracks_data: the dict containing all data on found tracks
    :return: a tuple, in which there is :
        - in first position the array of predictions for all tracks given in entry
        - in second position an array containing the IDs of the predicted tracks.
        - in third position the number of clusters
    """
    np_data = np.array(data)
    all_tracks = []
    for key in all_tracks_data.keys():
        all_tracks.append(all_tracks_data[key]['track'])
    np_all_tracks = np.array(all_tracks)

    dbscan_model = DBSCAN(min_samples=1).fit(np_all_tracks[:, :3])
    prediction = dbscan_predict(dbscan_model, np_data[:, :3])
    n_cluster = len(list(set(dbscan_model.labels_)))

    return prediction, np_data[:, -1], n_cluster


def dbscan_predict(model, X):
    """ Predicts an input list with a given db_scan model.

    :param model: the fitted dbscan model
    :param X: the list of samples that you wish to predict
    :return: a list containing the cluster for each input sample
    """

    nr_samples = X.shape[0]
    y_new = np.ones(shape=nr_samples, dtype=int) * -1

    for i in range(nr_samples):
        diff = model.components_ - X[i, :]  # NumPy broadcasting

        dist = np.linalg.norm(diff, axis=1)  # Euclidean distance

        shortest_dist_idx = np.argmin(dist)

        if dist[shortest_dist_idx] < model.eps:
            y_new[i] = model.labels_[
                model.core_sample_indices_[shortest_dist_idx]]
    return y_new
