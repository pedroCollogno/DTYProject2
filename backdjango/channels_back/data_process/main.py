
from sklearn.cluster import DBSCAN

import numpy as np

import utils.gps as gps
import utils.loading as loading
from utils.log import logger, create_new_folder
from utils.station_utils import *
from utils.track_utils import *

import json
import copy
import logging


import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D


def get_dbscan_prediction(data, all_tracks_data):
    """ Function that clusters data from TrackStreamEx objects

    :param data: The data to cluster using the dbscan algorithm
    :return: a tuple, in which there is :
        - in first position the array of predictions for all tracks given in entry
        - in second position an array containing the IDs of the predicted tracks.
    """
    np_data = np.array(data)
    all_tracks = []
    for key in all_tracks_data.keys():
        all_tracks.append(all_tracks_data[key]['track'])
    np_all_tracks = np.array(all_tracks)

    dbscan_model = DBSCAN(min_samples=1).fit(np_all_tracks[:, :3])
    prediction = dbscan_predict(dbscan_model, np_data[:, :3])
    n_cluster = len(dbscan_model.labels_)

    return prediction, np_data[:, 0], n_cluster


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


def main(*args, debug=False):
    """Main function, executes when the script is executed.

    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    """
    # prp_1 = "prod/station1.prp"
    # prp_2 = "prod/station2.prp"

    """
    prp_1 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/evf_sim/s1/TRC6420_ITRProduction_20181105_172929.prp"
    prp_2 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/evf_sim/s2/TRC6420_ITRProduction_20181105_172931.prp"
    prp_3 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/evf_sim/s3/TRC6420_ITRProduction_20181105_172932.prp"
    prp_4 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/evf_sim/s4/TRC6420_ITRProduction_20181105_172936.prp"
    """

    """
    prp_1 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/base_sim/s1/TRC6420_ITRProduction_20181026_143235.prp"
    prp_2 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/base_sim/s2/TRC6420_ITRProduction_20181026_143231.prp"
    prp_3 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/base_sim/s3/TRC6420_ITRProduction_20181026_143233.prp"
    """

    """
    prp_1 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/new_sim/s1/TRC6420_ITRProduction_20181107_165237.prp"
    prp_2 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/new_sim/s2/TRC6420_ITRProduction_20181107_165226.prp"
    prp_3 = "/Users/piaverous/Documents/DTY/Projet_Thales/thales-project/prod/new_sim/s3/TRC6420_ITRProduction_20181107_165213.prp"
    """
    if debug:
        logger.handlers[1].setLevel(logging.DEBUG)

    all_tracks_data = {}
    n = len(args[0])
    for i in range(1, n, 50):
        track_streams = []
        for arg in args:
            track_streams.append(arg[:i])
        logger.info(
            "\nMerging info from all stations... Reading %s sensor cycles..." % str(i-1))
        prev_tracks_data = copy.deepcopy(all_tracks_data)
        global_track_streams, all_tracks_data = fuse_all_station_tracks(
            *track_streams)
        logger.debug("Merge done !")
        make_emittor_clusters(global_track_streams,
                              all_tracks_data, prev_tracks_data, debug)


def make_emittor_clusters(global_track_streams, all_tracks_data, prev_tracks_data, debug=False):
    """ Makes the whole job of clustering emittors together from tracks

        Clusters emittors into networks using DBSCAN clustering algorithm. Updates the
        cluster id info in the all_tracks_data parameter. Sends information for each emittor
        directly to the Django backend.

    :param global_track_streams: All track streams to study
    :param all_tracks_data: Data on all tracks from global_track_streams, as a dictionnary
    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    """
    from backdjango.channels_back.back.views import send_emittor_to_front

    stations_data = []
    raw_tracks = []

    logger.debug("Taking track info out of %s track streams..." %
                 len(global_track_streams))
    for tracks in global_track_streams:
        raw_tracks = get_track_list_info(tracks, raw_tracks)
    logger.debug("Done !")
    logger.info("After merge of all station info, found a total of %s emittors." %
                len(raw_tracks))
    logger.debug("All_data_tracks has a total of %s emittors registered." %
                 len(all_tracks_data.keys()))

    if len(raw_tracks) > 1:
        y_pred, ids, n_cluster = get_dbscan_prediction(
            raw_tracks, all_tracks_data)
        i = 0
        for label in y_pred:
            track_id = get_track_id(raw_tracks[i])
            # Need to convert np.int64 to int for JSON format
            try:
                all_tracks_data[track_id]['network_id'] = int(label)
            except KeyError as err:
                logger.error("Keyerror on track %s : %s" % (i, raw_tracks[i]))
            i += 1
        logger.info("Found %s networks on the field.\n" % n_cluster)
        logger.info("Sending emittors through socket")
        for key in all_tracks_data.keys():
            if key not in prev_tracks_data.keys() and not debug:
                send_emittor_to_front(all_tracks_data[key])

    if debug:
        create_new_folder('tracks_json', '.')
        filename = './tracks_json/all_tracks_%s.json' % len(
            global_track_streams)
        logger.debug(
            "Found all of this data from tracks, writing it to %s" % filename)
        logger.debug("Wrote %s tracks to json file" %
                     len(all_tracks_data.keys()))
        with open(filename, 'w') as fp:
            json.dump(all_tracks_data, fp)

    if debug and len(raw_tracks) > 1:
        is_shown = False
        plt.ion()

        labels = []
        corresponding_batches = {}
        i = 0
        for label in y_pred:
            if label not in labels:
                labels.append(label)
                corresponding_batches[label] = []
            corresponding_batches[label].append(raw_tracks[i])
            track_id = get_track_id(raw_tracks[i])
            i += 1

        fig = plt.figure(1)

        ax = Axes3D(fig)

        colors = cm.rainbow(np.linspace(0, 1, n_cluster))
        logger.debug("\nResult of DBScan clustering on input data. There are %s inputs and %s clusters.\n" %
                     (len(raw_tracks), len(labels)))
        for key in corresponding_batches.keys():
            logger.debug("Label is %s" % key)
            for batch in corresponding_batches[key]:
                logger.debug("\tTrack data: % s" % batch)
            corresponding_batches[key] = np.array(corresponding_batches[key])
            ax.plot(corresponding_batches[key][:, 1], corresponding_batches[key][:, 0],
                    corresponding_batches[key][:, 3], '-o', color=colors[key])

        plt.draw()
        plt.pause(0.001)


"""This part runs if you run 'python main.py' in the console"""
if __name__ == '__main__':
    main(debug=True)
