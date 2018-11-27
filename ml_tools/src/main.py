

import numpy as np
import os

from .utils.log import logger, create_new_folder
from .utils.station_utils import *
from .utils.track_utils import *
from .utils.config import config
from .clustering.dbscan import *
from .deep_learning.processDL import process_data
from .deep_learning.model import test, train2

import json
import copy
import logging
import time

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

cycles_per_batch = config['VARS']['cycles_per_batch']


def main(*args, debug=False, sender_function=None, is_deep=True):
    """Main function, executes when the script is executed.

    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    ;param sender_function: 
    """

    if debug:
        logger.handlers[1].setLevel(logging.DEBUG)
    if sender_function is None:
        raise ValueError("No sender function, cannot interact with backend.")

    all_tracks_data = {}
    n = len(args[0])

    j = cycles_per_batch
    k = 1
    if is_deep:
        k = n-1
        j = 1

    for i in range(k, n, j):

        track_streams = []
        for arg in args:
            track_streams.append(arg[:i])

        logger.info(
            "\nMerging info from all stations... Reading %s sensor cycles... Last cycle is cycle n.%s" % (len(track_streams[0]), i))
        prev_tracks_data = copy.deepcopy(all_tracks_data)

        global_track_streams, all_tracks_data = fuse_all_station_tracks(
            *track_streams)
        logger.debug("Merge done !")
        make_emittor_clusters(global_track_streams,
                              all_tracks_data, prev_tracks_data, debug=debug, sender_function=sender_function, is_deep=is_deep)


def make_emittor_clusters(global_track_streams, all_tracks_data, prev_tracks_data, debug=False, sender_function=None, is_deep=False):
    """ Makes the whole job of clustering emittors together from tracks

        Clusters emittors into networks using DBSCAN clustering algorithm. Updates the
        cluster id info in the all_tracks_data parameter. Sends information for each emittor
        directly to the Django backend.

    :param global_track_streams: All track streams to study
    :param all_tracks_data: Data on all tracks from global_track_streams, as a dictionnary
    :param debug: (optional) default is to False, set to True to enter debug mode (more prints)
    """
    raw_tracks = []

    if sender_function is None:
        raise ValueError("No sender function, cannot interact with backend.")

    logger.info("Taking track info out of %s track streams..." %
                len(global_track_streams))
    for tracks in global_track_streams:
        raw_tracks = get_track_list_info(tracks, raw_tracks)
    logger.debug("Done !")
    logger.info("After merge of all station info, found a total of %s emittors." %
                len(raw_tracks))
    logger.info("All_data_tracks has a total of %s emittors registered." %
                len(all_tracks_data.keys()))

    if len(raw_tracks) > 1:
        if is_deep:
            file_name = str(time.time())
            process_data(global_track_streams, file_name)
            test(file_name)
            y_pred, ids = train2(file_name)
            n_cluster = len(set(y_pred))
        else:
            y_pred, ids, n_cluster = get_dbscan_prediction(
                raw_tracks, all_tracks_data)

        i = 0
        for label in y_pred:
            if is_deep:
                track_id = ids[i]
            else:
                track_id = get_track_id(raw_tracks[i])
            # Need to convert np.int64 to int for JSON format
            try:
                if int(label) is None:
                    raise ValueError(
                        "Network label is not defined for track %s" % track_id)
                all_tracks_data[track_id]['network_id'] = int(label)
                logger.warning("Label for track %s is %s" %
                               (track_id, int(label)))

            except (KeyError, ValueError) as err:
                logger.error("Error on track %s : \n\t%s" % (track_id, err))
            i += 1
        logger.info("Found %s networks on the field.\n" % n_cluster)
        logger.info("Sending emittors through socket")

        for key in all_tracks_data.keys():
            # if key not in prev_tracks_data.keys() and not debug:
            sender_function(all_tracks_data[key])

    if debug :
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
        plt.ion()

        labels = []
        corresponding_batches = {}
        i = 0
        for label in y_pred:
            if label not in labels:
                labels.append(label)
                corresponding_batches[label] = []
            corresponding_batches[label].append(raw_tracks[i])
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
