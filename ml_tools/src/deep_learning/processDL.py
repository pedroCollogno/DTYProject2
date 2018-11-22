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
import itertools

if __name__ == "__main__":
    # If launching this file as a file, enlarge the scope to see all of the src folder of ml_tools package
    file_dir = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(os.path.abspath(
        os.path.dirname(file_dir)))

from utils.loading import *
from utils.track_utils import *
from clustering.dbscan import get_dbscan_prediction_min


time_step_ms = 500


def removeFiles(directory):
    """ Removes all files from a directory

    :param directory: the directory from which files should be removed
    """
    filelist = [f for f in os.listdir(directory)]
    for f in filelist:
        os.remove(os.path.join(directory, f))


def checkPkl(file):
    """ TODO: COMPLETE DOCS

    :param file: TODO: COMPLETE DOCS
    """
    file_path = './pkl/{}'.format(sys.argv[1])
    df = pd.read_pickle('./pkl/{}'.format(sys.argv[1]))
    print(df)
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
        print(Y[k])
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


def predict_all_ids(tsexs):
    """ Uses DBSCAN to label all the networks

    :param station_1_track_stream: track stream for first station
    :return: a list of all the predictions and all the ids
    """
    raw_tracks = []
    stations_data = []
    for tsex in tsexs:
        raw_tracks = get_track_stream_ex_info(tsex, raw_tracks)
    y_pred, ids= get_dbscan_prediction_min(raw_tracks)
    stations_data.append([y_pred, ids])
    return [y_pred, ids]



def get_last_track_by_id(tsexs, id):
    """ Get the last track of an emitter

    :param tsexs: track stream to process
    :param id: id of the emitter to process
    :return: last track of an emitter
    """
    raw_tracks = []
    for tsex in tsexs:
        tracks = tsex.data.tracks
        for track in tracks:
            if get_track_id(track) == id:
                raw_tracks = get_track_info_with_alternates(track)
    return raw_tracks


def get_start_and_end(tsexs):
    """ Create a list of emission/nonemission at each time steps for an emitter

    :param tsexs: track stream to process
    :return start_date: start date of recording
    :return end_date: end date of recording
    :return sequence_size: number of time steps
    """
    raw_tracks = []
    for tsex in tsexs:
        tracks = tsex.data.tracks
        for track in tracks:
            raw_tracks.append(get_track_info_with_alternates(track))
    # raw_tracks : all the tracks with alternates info from a prp
    start_date = raw_tracks[0][6][0][0]
    end_date = raw_tracks[-1][6][0][1]
    sequence_size = (end_date-start_date)/time_step_ms
    return(start_date, end_date, sequence_size)


def get_steps_track(tsexs, id, sequence_size, start_date_ms):
    """ Create a list of emission/nonemission at each time steps for an emitter

    :param tsexs: track stream to process
    :param id: id of the emitter
    :param sequence_size: number of time steps
    :param start_date_ms: start date of recordingg
    :return: a list of 0 or 1, 0 is the emitter was not emitting, 1 if it was
    """
    last_track_id = get_last_track_by_id(tsexs, id)
    data = []
    for i in range(int(sequence_size)):
        found = 0
        for alternate in last_track_id[6]:
            if alternate[0] <= start_date_ms + i*time_step_ms <= alternate[1]:
                found = 1
                break
        data.append(found)
    return(data)


def process_data_clusters(tsexs, file_name):
    """ Process the data from the prp file and returns a network and steps object for each emittor,
    this prediction uses the dbscan

    :param tsexs: track stream to process
    :return: network and steps for each emittor
    """
    preds = predict_all_ids(tsexs)
    print(preds)

    temporal_data = get_start_and_end(tsexs)
    start_date_ms = temporal_data[0]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    print('Getting the steps from all the tracks')
    progress = 0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()
    for i in range(len(preds[0])):
        emitter_infos[preds[1][i]] = {
            "network": preds[0][i],
            "steps": get_steps_track(tsexs, preds[1][i], sequence_size, start_date_ms)
        }
        progress += 1
        pbar.update(progress)
        pbar.finish()
    return (emitter_infos)


def create_clusters():
    """
    Creates an object indexed by cluster id from the object indexed by emittor_id. Lets the user choose the PRP to process

    :return: Object indexed by cluster_id containing list of emittor_id and object indexed by emittor_id containing steps

    """
    root=tk.Tk()
    root.withdraw()
    file_path=filedialog.askopenfilename()
    tsexs= get_track_stream_exs_from_prp(file_path)
    ei=process_data_clusters(tsexs, file_path)

    i=0
    for k in ei:
        if ei[k]['network']>=i:
            i=ei[k]['network']
    clusters={}
    for k in range(i+1):
        clusters[k]=[]
    for k in ei:
        clusters[ei[k]['network']].append(k)
    return(clusters, ei)

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    #file_path = filedialog.askopenfilename()
    #tsexs = get_track_stream_exs_from_prp(file_path)
    #process_data(tsexs, file_path)
    create_clusters()

    # checkPkl(sys.argv[1])

def create_emittor_comparison_with_cluster(real_clusters, ei):
    """
    Uses the clusters from simulator data to build comparison between emittor and clusters for every possible tuple
    :param real_clusters: The clusters containing the emittor ids
    :param ei: The emittor infos, the vluster it belongs to and the steps of emissions
    :return: List of emissions of emittor and cluster and if the emittor belongs to the cluster
    """
    labels = []
    real_data = []
    print(real_clusters)
    for cluster in real_clusters:
        for emittor in real_clusters[cluster]:
            step_nb = len(ei[emittor]['steps'])
            for cluster_secondary in real_clusters:
                cluster_secondary_cumulated = [0 for k in range(step_nb)]
                if cluster == cluster_secondary:
                    label = True
                else:
                    label = False
                for emittor_secondary in real_clusters[cluster_secondary]:
                    if emittor != emittor_secondary:
                        cluster_secondary_cumulated = [int(
                            cluster_secondary_cumulated[k] or ei[emittor_secondary]['steps'][k]) for k in range(step_nb)]
                if not (len(real_clusters[cluster])==1 and cluster_secondary==cluster):
                    for sequence_iterator in range(step_nb//50):
                        real_data.append([ei[emittor]['steps'][sequence_iterator*50:(sequence_iterator+1)*50],
                                            cluster_secondary_cumulated[sequence_iterator*50:(sequence_iterator+1)*50]])
                        labels.append(label)
                else:
                    print("1 emittor cluster comparing with itself")
    return(real_data, labels)
