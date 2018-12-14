import itertools
import argparse
import shutil
import sys
import os

import tkinter as tk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from tkinter import filedialog
from sklearn.cluster import DBSCAN
from progressbar import ProgressBar

import matplotlib
matplotlib.use("TkAgg")

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from ..utils import config
from ..utils.log import create_new_folder
from ..utils.loading import get_track_streams_from_prp
from ..utils.track_utils import get_track_stream_info, get_track_info, get_track_id, get_track_list_info
from ..clustering.dbscan import get_dbscan_prediction_min

import logging
logger = logging.getLogger('backend')

time_step_ms = config['VARS']['time_step_ms']
PKL_DIR = config['PATH']['pkl']

def get_track_info_with_alternates(track):
    """ Takes essential information out of a given track

    :param track: the track from which info should be extracted
    :return: a list containing the basic info of the track :
        [track_id, measurement_type, central_freq_hz,
            bandwitdh_hz, average_azimut_deg, list of alternates : [start_date, end_date]]
    """
    new_info_from_track = get_track_info(track)
    alternates_list = []
    for alternate in track.alternates:
        alternates_list.append(
            [alternate.start.date_ms, (alternate.start.date_ms + alternate.duration_us/1000)])
    new_info_from_track.append(alternates_list)
    return new_info_from_track


def predict_all_ids(track_streams):
    """ Uses DBSCAN to label all the networks

    :param track_streams: track stream for stations
    :return: a list of all the predictions and all the ids
    """
    raw_tracks = []
    for track_stream in track_streams:
        raw_tracks = get_track_list_info(track_stream, raw_tracks)
    y_pred, ids = get_dbscan_prediction_min(raw_tracks)
    return [y_pred, ids]


def get_last_track_by_id(track_streams, id):
    """ Get the last track of an emitter

    :param track_streams: track stream to process
    :param id: id of the emitter to process
    :return: last track of an emitter
    """
    raw_tracks = []
    for track_stream in track_streams:
        for track in track_stream:
            if get_track_id(track) == id:
                raw_tracks = get_track_info_with_alternates(track)
                print(len(raw_tracks[6]))
                print(raw_tracks[6][-1])
    return raw_tracks


def get_start_and_end(track_streams):
    """ Get the start date, end date and sequence size given a time step

    :param track_streams: track stream to process
    :return start_date: start date of recording
    :return end_date: end date of recording
    :return sequence_size: number of time steps
    """
    raw_tracks = []
    for track_stream in track_streams:
        for track in track_stream:
            raw_tracks.append(get_track_info_with_alternates(track))
    # raw_tracks : all the tracks with alternates info from a prp
    start_date = raw_tracks[0][6][0][0] # 0 : first track ever, 6 : list of alternates, 0: first alternate, 0: begin date
    end_date = raw_tracks[-1][6][0][1] # -1 : last track ever, 6 : list of alternates, 0 : first alternate (alternates are added at the beginning of the list), 1 : end date
    sequence_size = (end_date-start_date)/time_step_ms
    return(start_date, end_date, sequence_size)


def get_steps_track(track_streams, id, sequence_size, start_date_ms):
    """ Create a list of emission/nonemission at each time steps for an emitter

    :param track_streams: track stream to process
    :param id: id of the emitter
    :param sequence_size: number of time steps
    :param start_date_ms: start date of recording
    :return: a list of 0 or 1, 0 is the emitter was not emitting, 1 if it was
    """
    last_track_id = get_last_track_by_id(track_streams, id)
    data = []
    for i in range(int(sequence_size)):
        found = 0
        for alternate in last_track_id[6]:
            if alternate[0] <= (start_date_ms + i*time_step_ms) and (start_date_ms + i*time_step_ms)  <= alternate[1]:
                found = 1
                break
        data.append(found)
    return(data)


def process_data(track_streams, file_name):
    """ Process the data from the prp file into a dataframe that can be used in the deep learning models.

    :param track_streams: track stream to process
    :param file_name: file name of the pkl file in /pkl where data will be saved
    """
    if isinstance(track_streams[0], list):
        ts = track_streams
    else:
        ts = [track_stream.tracks for track_stream in track_streams]

    preds = predict_all_ids(ts)

    temporal_data = get_start_and_end(ts)
    start_date_ms = temporal_data[0]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    logger.info('Getting the steps from all the tracks')
    progress = 0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()

    # Create a dict :
    # emitter_infos : {
    #       emitterId: {
    #           networkId : ...,
    #           steps : [0,0,1,1,1,...,1,1,0,0,0] e.g.          
    #   }
    # }
    for i in range(len(preds[0])):
        emitter_infos[preds[1][i]] = {
            "network": preds[0][i],
            "steps": get_steps_track(ts, preds[1][i], sequence_size, start_date_ms)
        }
        progress += 1
        pbar.update(progress)
        pbar.finish()

    X = []
    Y = []
    id_Couple = []
    logger.info('Processing data')
    progress = 0
    pbar2 = ProgressBar(maxval=(len(preds[0])*len(preds[0]))/2)
    pbar2.start()

    create_new_folder(file_name, PKL_DIR)
    path_to_save = os.path.join(PKL_DIR, file_name)

    # For each possible couple of emittors, transforms their steps lists (2 lists of size n) in one list of lists (of size (n, 2)) named 'X'
    # Adds X, Y (the label, 1 if the emittors are in the same network, else 0), and id_Couple : (idEmitter1, idEmitter2)
    for couple in itertools.combinations(preds[1], 2):
        Y_value = int(emitter_infos[couple[0]]["network"]
                      == emitter_infos[couple[1]]["network"])
        steps1 = emitter_infos[couple[0]]["steps"]
        steps2 = emitter_infos[couple[1]]["steps"]
        X_value = []
        for i in range(int(sequence_size)):
            X_value.append([steps1[i], steps2[i]])
        X.append(X_value)
        Y.append(Y_value)
        id_Couple.append([couple[0], couple[1]])
        progress += 1
        # We save the data in seperated files every 2000 possible couples (to avoid too big dataframes) (the separated files will be loaded altogether in model.py)
        if progress % 2000 == 0:
            df = pd.DataFrame(
                {
                    'X': X,
                    'Y': Y,
                    'id_Couple': id_Couple
                }, columns=['X', 'Y', 'id_Couple'])
            name = '{0}_{1}.pkl'.format(file_name, progress)
            df.to_pickle(os.path.join(path_to_save, name))
            X = []
            Y = []
            id_Couple = []
            logger.info("Pickle saved in {0}".format(
                os.path.join(path_to_save, name)))
        pbar2.update(progress)
    df = pd.DataFrame(
        {
            'X': X,
            'Y': Y,
            'id_Couple': id_Couple
        }, columns=['X', 'Y', 'id_Couple'])

    name = '{0}_{1}.pkl'.format(file_name, progress)
    df.to_pickle(os.path.join(path_to_save, name))

    X = []
    Y = []
    id_Couple = []
    logger.info("Pickle saved in {0}".format(
        os.path.join(path_to_save, name)))
    pbar2.finish()


def create_clusters(track_streams, y_pred=None, ids=None):
    """ Creates an object indexed by cluster id from the object indexed by emitter_id. Lets the user choose the PRP to process

    :param track_streams: the track streams to build into clusters
    :return: Object indexed by cluster_id containing list of emitter_id and object indexed by emitter_id containing steps
    """

    ei = process_data_clusters(track_streams, preds=[y_pred, ids])

    i = 0
    for k in ei:
        if ei[k]['network'] >= i:
            i = ei[k]['network']
    clusters = {}
    for k in ei:
        if ei[k]['network'] not in clusters.keys():
            clusters[ei[k]['network']] = []
        clusters[ei[k]['network']].append(k)

    return(clusters, ei)


def input_confirmation():
    """
    Asks to prompt confirmation for an command line operation.

    :return: True if the operation is confirmed, False otherwise
    """
    logger.info("Do you want to continue ? (y/[n])")
    choice = input().lower()
    if choice == "y" or choice == "yes":
        return True
    else:
        return False


def process_data_clusters(track_streams, preds=None):
    """ Creates a dictionnary of emitters containing their network and the list of sampled emissions

    :param track_streams: track stream to process
    :return: dictionnary of emitters containing their network and the list of sampled emissions
    """
    if preds is None:
        preds = predict_all_ids(track_streams)

    test_ids = set(preds[1])
    logger.debug("Number of emitters :", len(test_ids), len(preds[1]))

    temporal_data = get_start_and_end(track_streams)
    start_date_ms = temporal_data[0]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    logger.info('Getting the steps from all the tracks.')
    progress = 0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()
    for i in range(len(preds[0])):
        track = get_last_track_by_id(track_streams, preds[1][i])
        if track[0] != 3:  # Only work with track if it's not a BURST type.
            emitter_infos[preds[1][i]] = {
                "network": preds[0][i],
                "steps": get_steps_track(track_streams, preds[1][i], sequence_size, start_date_ms)
            }
        progress += 1
        pbar.update(progress)
        pbar.finish()

    return (emitter_infos)


def create_emitter_comparison_with_cluster(real_clusters, ei):
    """
    Uses the clusters from simulator data to build comparison between emitter and clusters for every possible tuple
    :param real_clusters: The clusters containing the emitter ids
    :param ei: The emitter infos, the vluster it belongs to and the steps of emissions
    :return: List of emissions of emitter and cluster and if the emitter belongs to the cluster
    """
    labels = []
    real_data = []
    for cluster in real_clusters:
        for emitter in real_clusters[cluster]:
            step_nb = len(ei[emitter]['steps']) - \
                (len(ei[emitter]['steps']) % 50)
            for cluster_secondary in real_clusters:
                cluster_secondary_cumulated = [
                    0 for k in range(len(ei[emitter]['steps']))]
                if cluster == cluster_secondary:
                    label = True
                else:
                    label = False
                for emitter_secondary in real_clusters[cluster_secondary]:
                    if emitter != emitter_secondary:
                        cluster_secondary_cumulated = [int(
                            cluster_secondary_cumulated[k] or ei[emitter_secondary]['steps'][k]) for k in range(step_nb)]
                if not (len(real_clusters[cluster]) == 1 and cluster_secondary == cluster):
                    for sequence_iterator in range(step_nb//50):
                        real_data.append([ei[emitter]['steps'][sequence_iterator*50:(sequence_iterator+1)*50],
                                          cluster_secondary_cumulated[sequence_iterator*50:(sequence_iterator+1)*50]])
                        labels.append(label)
                else:
                    logger.info("1 emitter cluster comparing with itself")
    return(real_data, labels, step_nb)


def create_cheat_comparison_with_cluster(real_clusters, ei):
    """ Uses the clusters from simulator data to build comparison between emitter and clusters for every possible tuple

    :param real_clusters: The clusters containing the emitter ids
    :param ei: The emitter infos, the vluster it belongs to and the steps of emissions
    :return: List of emissions of emitter and cluster and if the emitter belongs to the cluster
    """
    labels = []
    real_data = []
    for cluster in real_clusters:
        for emitter in real_clusters[cluster]:
            step_nb = len(ei[emitter]['steps']) - \
                (len(ei[emitter]['steps']) % 50)

            for cluster_secondary in real_clusters:
                cluster_secondary_cumulated = [0 for k in range(step_nb)]
                label = True
                for emitter_secondary in real_clusters[cluster_secondary]:
                    if emitter != emitter_secondary:
                        cluster_secondary_cumulated = [int(
                            cluster_secondary_cumulated[k] or ei[emitter_secondary]['steps'][k]) for k in range(step_nb)]

                        for k in range(step_nb):
                            if ei[emitter]['steps'][k]+ei[emitter_secondary]['steps'][k] == 2:
                                label = False

                if not (len(real_clusters[cluster]) == 1 and cluster_secondary == cluster):
                    for sequence_iterator in range(step_nb//50):
                        real_data.append([ei[emitter]['steps'][sequence_iterator*50:(sequence_iterator+1)*50],
                                          cluster_secondary_cumulated[sequence_iterator*50:(sequence_iterator+1)*50]])
                        labels.append(label)
                else:
                    logger.info("1 emitter cluster comparing with itself")
    return(real_data, labels, step_nb)


def create_comparison_one_to_one(emitter_id,  emissions, ids_in_cluster, sequence_size):
    """
    Creates list of data to use the model's prediction (e.g: the emission activity of the cluster and the emitter's emission activity), 
    samples the emissions based on sequence_size.
    :param emitter_id: The emitter's id to be compared with the cluster
    :param emissions: The list of emissions of all the emitters
    :param ids_in_cluster: List of emitters ids in the cluster you want to compare with the emitter
    :param sequence_size: The size of the sequence you want to compare
    """
    list_of_data = []
    step_nb = len(emissions[emitter_id]['steps']) - \
        (len(emissions[emitter_id]['steps']) % sequence_size)
    cluster_secondary_cumulated = [0 for k in range(step_nb)]
    for emitter_secondary in ids_in_cluster:
        if emitter_secondary != emitter_id:
            cluster_secondary_cumulated = [int(
                cluster_secondary_cumulated[k] or emissions[emitter_secondary]['steps'][k]) for k in range(step_nb)]
    for sequence_iterator in range(step_nb//sequence_size):
        list_of_data.append([emissions[emitter_id]['steps'][sequence_iterator*sequence_size:(sequence_iterator+1)
                                                            * sequence_size], cluster_secondary_cumulated[sequence_iterator*sequence_size:(sequence_iterator+1)*sequence_size]])
    return(list_of_data, step_nb)


def main(file_path, file_name):
    """
    Main function. Launches this scrpt with the given arguments.

    :param file_path: the path to the .PRP files to process
    :param file_name: the name of the .PKL file to create
    """
    track_streams = get_track_streams_from_prp(file_path)
    process_data(track_streams, file_name)
    # checkPkl(file_name)


"""This part runs if you run 'python processDL.py pkl_name' in the console
    :param 1: name of prp file in /prod to load
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Process the data from the prp file into a dataframe that can be used in the deep learning models")
    parser.add_argument('--name', metavar='path', required=False,
                        help='The name of the file to create to store the data')
    args = parser.parse_args()

    # If a run with the same name as the inputed one is found
    if os.path.exists(os.path.join(PKL_DIR, args.name)):
        logger.info(
            "A previous run exists with this name : %s. Proceeding wil erase it." % args.name)
        result = input_confirmation()
        if result:
            shutil.rmtree(os.path.join(PKL_DIR, args.name))
        else:
            raise ValueError("You cannot overwrite this run : %s" % args.name)

    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.update()
    track_streams = get_track_streams_from_prp(file_path)

    create_clusters(track_streams)

    # checkPkl(sys.argv[1])
    main(file_path, args.name)
