import matplotlib
matplotlib.use("TkAgg")

from progressbar import ProgressBar
from sklearn.cluster import DBSCAN
from tkinter import filedialog

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk

import os
import sys
import shutil
import argparse
import itertools

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from ..utils import config
from ..utils.log import create_new_folder, logger
from ..utils.loading import get_track_streams_from_prp
from ..utils.track_utils import get_track_stream_info, get_track_info, get_track_id, get_track_list_info
from ..clustering.dbscan import get_dbscan_prediction_min


time_step_ms = config['VARS']['time_step_ms']
PKL_DIR = config['PATH']['pkl']


def checkPkl(file_name):
    file_path = os.path.join(PKL_DIR, file_name)
    df = pd.read_pickle(file_path)
    logger.info(df)
    df = df.loc[df['Y'] == 1]
    X = df['X'].values
    Y = df['Y'].values
    for k in range(len(X)):
        comparaisons = X[k]
        emitter1 = []
        emitter2 = []
        for i in range(len(comparaisons)):
            emitter1.append(comparaisons[i][0])
            emitter2.append(comparaisons[i][1])

        plt.figure(1)
        plt.plot(emitter1, color='green')

        plt.plot(emitter2, color='blue')
        logger.info(Y[k])
        plt.show()


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

    :param station_1_track_stream: track stream for first station
    :return: a list of all the predictions and all the ids
    """
    raw_tracks = []
    stations_data = []
    for track_stream in track_streams:
        raw_tracks = get_track_list_info(track_stream, raw_tracks)
    y_pred, ids = get_dbscan_prediction_min(raw_tracks)
    stations_data.append([y_pred, ids])
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
    return raw_tracks


def get_start_and_end(track_streams):
    """ Create a list of emission/nonemission at each time steps for an emitter

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
    start_date = raw_tracks[0][6][0][0]
    end_date = raw_tracks[-1][6][0][1]
    sequence_size = (end_date-start_date)/time_step_ms
    return(start_date, end_date, sequence_size)


def get_steps_track(track_streams, id, sequence_size, start_date_ms):
    """ Create a list of emission/nonemission at each time steps for an emitter

    :param track_streams: track stream to process
    :param id: id of the emitter
    :param sequence_size: number of time steps
    :param start_date_ms: start date of recordingg
    :return: a list of 0 or 1, 0 is the emitter was not emitting, 1 if it was
    """
    last_track_id = get_last_track_by_id(track_streams, id)
    data = []
    for i in range(int(sequence_size)):
        found = 0
        for alternate in last_track_id[6]:
            if alternate[0] <= start_date_ms + i*time_step_ms <= alternate[1]:
                found = 1
                break
        data.append(found)
    return(data)


def process_data(track_streams, file_name):
    """ Process the data from the prp file into a dataframe that can be used in the deep learning models.

    :param track_streams: track stream to process
    :param file_name: file name of the pkl file in /pkl where data will be saved
    """
    preds = predict_all_ids(track_streams)
    test_ids = set(preds[1])
    #print("Number of emitters :", len(test_ids), len(preds[1]))

    temporal_data = get_start_and_end(track_streams)
    start_date_ms = temporal_data[0]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    logger.info('Getting the steps from all the tracks')
    progress = 0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()
    for i in range(len(preds[0])):
        emitter_infos[preds[1][i]] = {
            "network": preds[0][i],
            "steps": get_steps_track(track_streams, preds[1][i], sequence_size, start_date_ms)
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
    :param 2: name of pkl file that will be saved in /pkl
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Process the data from the prp file into a dataframe that can be used in the deep learning models")
    parser.add_argument('--name', metavar='path', required=True,
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
    root.destroy()

    main(file_path, args.name)
