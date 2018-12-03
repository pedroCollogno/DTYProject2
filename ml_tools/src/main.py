

import numpy as np
import os

from .utils.log import create_new_folder
from .utils.station_utils import *
from .utils.track_utils import *
from .utils.config import config
from .clustering.dbscan import *
from .deep_learning.processDL import process_data, create_clusters
from .deep_learning.model import test, train2
from .deep_learning.model_clusters import ModelHandler

import json
import copy
import logging
import time

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D
from keras import backend as K

import logging
logger = logging.getLogger('backend')

cycles_per_batch = config['VARS']['cycles_per_batch']
LOGS_DIR = config['PATH']['logs']


class EWHandler:
    """
    Handler class, used to process data coming from Electronic Warfare.
    """

    def __init__(self):
        """
        Initiate the EWHandler object
        """
        self.running = False
        self.paused = False
        self.total_duration = 0
        self.progress = 0
        self.model_handler = None

    def stop(self):
        """
        Stops the current instance of this object, ie. stops sending emittors and clustering them.
        """
        self.running = False

    def pause(self):
        """
        Pauses the current instance of this object, ie. stops sending emittors and clustering them.
        """
        self.paused = True

    def play(self):
        """
        Restarts the current instance of this object after a pause.
        """
        self.paused = False

    def main(self, *args, debug=False, sender_function=None, use_deep=False, mix=False):
        """Main function.

        :param debug: (optional) default is to False, set to True to enter debug mode (more logs)
        :param sender_function: the function used to send emittors to a frontend.
            This function is not defined in this package, and can be of any kind.
        :param use_deep: boolean to know if clustering should be done using deep learning or not (using DBScan clustering)
        :param mix: boolean to know if clustering should use a complementary mix of DB_Scan and Deep Learning methods
        """
        self.running = True
        self.paused = False

        if debug:
            logger.handlers[1].setLevel(logging.DEBUG)
        if sender_function is None:
            raise ValueError(
                "No sender function, cannot interact with backend.")

        all_tracks_data = {}
        self.total_duration = len(args[0])

        j = cycles_per_batch
        k = 1
        if use_deep and not mix:
            k = self.total_duration-1
            j = 1
        elif mix:
            j = 100
            self.model_handler = ModelHandler()

        self.progress = k
        while self.progress < self.total_duration and self.running:
            while self.paused:
                time.sleep(0.5)

            track_streams = []
            for arg in args:
                track_streams.append(arg[:self.progress])
            logger.info(
                "\nMerging info from all stations... Reading %s sensor cycles... Last cycle is cycle n.%s" % (len(track_streams[0]), self.progress))
            prev_tracks_data = copy.deepcopy(all_tracks_data)

            global_track_streams, all_tracks_data = fuse_all_station_tracks(
                *track_streams)

            logger.debug("Merge done !")

            self.make_emittor_clusters(global_track_streams,
                                       all_tracks_data, prev_tracks_data, debug=debug, sender_function=sender_function, use_deep=use_deep, mix=mix)
            self.progress += j
            time.sleep(0.5)
        K.clear_session()

    def make_emittor_clusters(self, global_track_streams, all_tracks_data, prev_tracks_data, debug=False, sender_function=None, use_deep=False, mix=False):
        """ Makes the whole job of clustering emittors together from tracks

            Clusters emittors into networks using DBSCAN clustering algorithm. Updates the
            cluster id info in the all_tracks_data parameter. Sends information for each emittor
            directly to the Django backend.

        :param global_track_streams: All track streams to study
        :param all_tracks_data: Data on all tracks from global_track_streams, as a dictionnary
        :param prev_tracks_data: Data from all tracks from previous cycle batch
        :param debug: (optional) default is to False, set to True to enter debug mode (more logs)
        :param sender_function: the function used to send emittors to a frontend.
            This function is not defined in this package, and can be of any kind.
        :param use_deep: boolean to know if clustering should be done using deep learning or not (using DBScan clustering)
        :param mix: boolean to know if clustering should use a complementary mix of DB_Scan and Deep Learning methods
        """
        raw_tracks = []

        if sender_function is None:
            raise ValueError(
                "No sender function, cannot interact with backend.")

        logger.info("Taking track info out of %s track streams..." %
                    len(global_track_streams))
        for tracks in global_track_streams:
            raw_tracks = get_track_list_info(tracks, raw_tracks)
        logger.debug("Done !")
        logger.info("After merge of all station info, found a total of %s emittors." %
                    len(raw_tracks))
        logger.info("All_data_tracks has a total of %s emittors registered." %
                    len(all_tracks_data.keys()))

        if len(raw_tracks) > 1 and self.running:
            if use_deep and not mix:
                file_name = str(time.time())
                process_data(global_track_streams, file_name)
                test(file_name)
                y_pred, ids = train2(file_name)
                n_cluster = len(set(y_pred))
            elif mix:
                y_pred, ids, n_cluster = get_dbscan_prediction(
                    raw_tracks, all_tracks_data)
                clusters, ei = create_clusters(
                    global_track_streams, y_pred=y_pred, ids=ids)

                for emittor_id in ei:
                    possible_scores = {}
                    for cluster_id in clusters:
                        emittor_in_cluster = self.model_handler.are_in_same_cluster(
                            emittor_id, cluster_id, ei, clusters)
                        possible_scores[cluster_id] = emittor_in_cluster

                    min_score_cluster = min(
                        possible_scores, key=possible_scores.get)
                    all_tracks_data[emittor_id]['possible_network'] = min_score_cluster
                    logger.warning("Emittor %s is pretty close to cluster %s !" % (
                        emittor_id, min_score_cluster))

            else:
                y_pred, ids, n_cluster = get_dbscan_prediction(
                    raw_tracks, all_tracks_data)

            i = 0

            if len(y_pred) > len(all_tracks_data.keys()):
                err = "Too many labels : Got %s labels for %s emittors" % (
                    len(y_pred), len(all_tracks_data.keys()))
                logger.error(err)
                raise ValueError(err)

            for label in y_pred:
                if use_deep:
                    track_id = ids[i]
                else:
                    track_id = get_track_id(raw_tracks[i])
                # Need to convert np.int64 to int for JSON format
                all_tracks_data[track_id]['network_id'] = int(label)
                all_tracks_data[track_id]['total_duration'] = self.total_duration
                all_tracks_data[track_id]['progress'] = self.progress
                i += 1
            logger.info("Found %s networks on the field.\n" % n_cluster)
            logger.info("Sending emittors through socket")

            # for key in all_tracks_data.keys():
            # if key not in prev_tracks_data.keys() and not debug:

            # sender_function(all_tracks_data[key])
            sender_function(all_tracks_data)

        if debug:
            create_new_folder('tracks_json', LOGS_DIR)
            name = 'all_tracks_%s.json' % len(
                global_track_streams)
            file_path = os.path.join(LOGS_DIR, 'tracks_json', name)
            logger.debug(
                "Found all of this data from tracks, writing it to %s" % file_path)
            logger.debug("Wrote %s tracks to json file" %
                         len(all_tracks_data.keys()))
            with open(file_path, 'w') as fp:
                json.dump(all_tracks_data, fp)


"""This part runs if you run 'python main.py' in the console"""
if __name__ == '__main__':
    main(debug=True)
