
from sklearn.cluster import DBSCAN

import numpy as np

import utils.gps as gps
import utils.loading as loading
from utils.log import logger
from utils.station_utils import *
from utils.track_utils import *

import json
import logging

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D


def get_dbscan_prediction(data):
    """ Function that clusters data from TrackStreamEx objects

    :param data: The data to cluster using the dbscan algorithm
    :return: a tuple, in which there is :
        - in first position the array of predictions for all tracks given in entry
        - in second position an array containing the IDs of the predicted tracks.
    """
    np_data = np.array(data)
    prediction = DBSCAN(min_samples=1).fit_predict(np_data[:, :3])
    return prediction, np_data[:, 0]


def main(debug=False):
    """Main function, executes when the script is executed.

    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    """
    # prp_1 = "prod/station1.prp"
    # prp_2 = "prod/station2.prp"
    """
    prp_1 = "prod/evf_sim/s1/TRC6420_ITRProduction_20181105_172929.prp"
    prp_2 = "prod/evf_sim/s2/TRC6420_ITRProduction_20181105_172931.prp"
    prp_3 = "prod/evf_sim/s3/TRC6420_ITRProduction_20181105_172932.prp"
    prp_4 = "prod/evf_sim/s4/TRC6420_ITRProduction_20181105_172936.prp"
    """

    """
    prp_1 = "prod/s1/TRC6420_ITRProduction_20181026_143235.prp"
    prp_2 = "prod/s2/TRC6420_ITRProduction_20181026_143231.prp"
    prp_3 = "prod/s3/TRC6420_ITRProduction_20181026_143233.prp"
    """

    prp_1 = "prod/new_sim/s1/TRC6420_ITRProduction_20181107_165237.prp"
    prp_2 = "prod/new_sim/s2/TRC6420_ITRProduction_20181107_165226.prp"
    prp_3 = "prod/new_sim/s3/TRC6420_ITRProduction_20181107_165213.prp"

    if debug:
        logger.handlers[1].setLevel(logging.DEBUG)

    tsexs_1 = loading.get_track_stream_exs_from_prp(prp_1)
    tsexs_2 = loading.get_track_stream_exs_from_prp(prp_2)
    tsexs_3 = loading.get_track_stream_exs_from_prp(prp_3)

    sync_stations(tsexs_1, tsexs_2, tsexs_3)

    n = len(tsexs_1)
    k = 1
    for i in range(k, n):
        logger.info(
            "\nMerging info from all stations... Reading %s sensor cycles..." % str(i-k))
        global_track_streams, all_tracks_data = fuse_all_station_tracks(
            tsexs_1[:i], tsexs_2[:i], tsexs_3[:i])
        logger.debug("Merge done !")
        make_emittor_clusters(global_track_streams, all_tracks_data, debug)
        k = max(1, i-100)


def make_emittor_clusters(global_track_streams, all_tracks_data, debug=False):
    """ Makes the whole job of clustering emittors together from tracks

        Clusters emittors into networks using DBSCAN clustering algorithm. Updates the
        cluster id info in the all_tracks_data parameter. Sends information for each emittor
        directly to the Django backend.

    :param global_track_streams: All track streams to study
    :param all_tracks_data: Data on all tracks from global_track_streams, as a dictionnary
    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    """
    stations_data = []
    raw_tracks = []

    k = max(len(global_track_streams) - 100, 0)

    logger.debug("Taking track info out of %s track streams..." %
                 str(len(global_track_streams)-k))
    for tracks in global_track_streams[k:]:
        raw_tracks = get_track_list_info(tracks, raw_tracks)
    logger.debug("Done !")
    logger.info("After merge of all station info, found a total of %s emittors." %
                len(raw_tracks))

    if len(raw_tracks) > 1:
        y_pred, ids = get_dbscan_prediction(raw_tracks)
        i = 0
        for label in y_pred:
            track_id = get_track_id(raw_tracks[i])
            # Need to convert np.int64 to int for JSON format
            all_tracks_data[track_id]['network_id'] = int(label)
            i += 1
        n_clusters = max(y_pred) + 1
        logger.info("Found %s networks on the field.\n" % n_clusters)

    filename = 'tracks/all_tracks_%s.json' % len(global_track_streams)
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
            all_tracks_data[track_id]['network_id'] = label
            i += 1

        fig = plt.figure(1)
        ax = Axes3D(fig)
        colors = cm.rainbow(np.linspace(0, 1, len(y_pred)))
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
    main(debug=False)
