import utils as utils
import numpy as np
import itertools
from progressbar import ProgressBar
import pandas as pd
import sys
import csv
import os
import matplotlib.pyplot as plt


time_step_ms = 500

def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print ('Error: Creating directory. ' + directory)

def removeFiles(directory):
    filelist = [ f for f in os.listdir(directory)]
    for f in filelist:
        os.remove(os.path.join(directory, f))

def checkPkl(file):
    file_path = './pkl/{}'.format(sys.argv[1])
    df = pd.read_pickle('./pkl/{}'.format(sys.argv[1]))
    print(df)
    df = df.loc[df['Y'] == 1]
    X = df['X'].values
    Y = df['Y'].values
    for k in range (len(X)):
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

    # for i in range(2):

    #     key_indice = 1
    #     y_labels = []
    #     y_ticks = []
    #     for key in all_alternates["prp{}".format(i+1)]:
    #         boxes = []
    #         for alternate in all_alternates["prp{}".format(i+1)][key]:
    #             boxes.append((alternate.start.date_ms/(1000),
    #                           alternate.duration_us/1000000))
    #         ax[i].broken_barh(boxes, (key_indice, 0.9), facecolors='blue')
    #         y_ticks.append(key_indice)
    #         y_labels.append(str(key))
    #         key_indice += 1
    #     ax[i].set_yticks(y_ticks)
    #     ax[i].set_yticklabels(y_labels)
    #     ax[i].set_ylabel("Id")
    #     ax[i].set_xlabel("Seconds")
    # plt.show()




def get_track_info_with_alternates(track):
    """ Takes essential information out of a given track

    :param track: the track from which info should be extracted
    :return: a list containing the basic info of the track :
        [track_id, measurement_type, central_freq_hz,
            bandwitdh_hz, average_azimut_deg, list of alternates : [start_date, end_date]]
    """
    new_info_from_track = utils.get_track_info(track)
    alternates_list = []
    for alternate in track.alternates:
        alternates_list.append([alternate.start.date_ms, (alternate.start.date_ms + alternate.duration_us/1000)])
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
        raw_tracks = utils.get_track_stream_ex_info(tsex, raw_tracks)
    y_pred, ids = utils.get_dbscan_prediction(raw_tracks)
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
            if track.id.most_significant == id: 
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
    start_date = raw_tracks[0][5][0][0]
    end_date = raw_tracks[-1][5][0][1]
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
        for alternate in last_track_id[5]:
            if alternate[0] <= start_date_ms + i*time_step_ms <= alternate[1]:
                found = 1
                break
        data.append(found)
    return(data)

def process_data(tsexs, file_name):
    """ Process the data from the prp file into a dataframe that can be used in the deep learning models.

    :param tsexs: track stream to process
    :param file_name: file name of the pkl file in /pkl where data will be saved
    """
    preds = predict_all_ids(tsexs)

    temporal_data = get_start_and_end(tsexs)
    start_date_ms = temporal_data[0]
    sequence_size = temporal_data[2]

    emitter_infos = {}
    print('Getting the steps from all the tracks')
    progress=0
    pbar = ProgressBar(maxval=(len(preds[0])))
    pbar.start()
    for i in range (len(preds[0])):
        emitter_infos[preds[1][i]] = {
            "network" : preds[0][i],
            "steps" : get_steps_track(tsexs, preds[1][i], sequence_size, start_date_ms)
        }
        progress+=1
        pbar.update(progress)
        pbar.finish()
    print(len(emitter_infos))

    X = []
    Y = []
    print('Processing data')
    progress = 0
    pbar2 = ProgressBar(maxval=(len(preds[0])*len(preds[0]))/2)
    pbar2.start()

    createFolder('./pkl/{}'.format(file_name))
    removeFiles('./pkl/{}'.format(file_name))

    for couple in itertools.combinations(preds[1],2):
        Y_value = int(emitter_infos[couple[0]]["network"]==emitter_infos[couple[1]]["network"])
        steps1 = emitter_infos[couple[0]]["steps"]
        steps2 = emitter_infos[couple[1]]["steps"]
        X_value = []
        for i in range (int(sequence_size)):
            X_value.append([steps1[i], steps2[i]]) 
        X.append(X_value)
        Y.append(Y_value)
        progress += 1
        if progress%2000 == 0:
            df = pd.DataFrame(
                {
                    'X' : X,
                    'Y' : Y
                }, columns = ['X', 'Y'])
            df.to_pickle('./pkl/{0}/{1}_{2}.pkl'.format(file_name, file_name, progress))
            X=[]
            Y=[]
            print("Pickle saved in /pkl/{0}/{1}_{2}.pkl".format(file_name, file_name, progress))
        pbar2.update(progress)
    df = pd.DataFrame(
                {
                    'X' : X,
                    'Y' : Y
                }, columns = ['X', 'Y'])
    df.to_pickle('./pkl/{0}/{1}_{2}.pkl'.format(file_name, file_name, progress))
    X=[]
    Y=[]
    print("Pickle saved in /pkl/{0}/{1}_{2}.pkl".format(file_name, file_name, progress))
    pbar2.finish()

"""This part runs if you run 'python processDL.py prp_name pkl_name' in the console
    :param 1: name of prp file in /prod to load
    :param 2: name of pkl file that will be saved in /pkl
"""
if __name__ == '__main__':
    tsexs = utils.get_track_stream_exs_from_prp("prod/{}.prp".format(sys.argv[1]))
    process_data(tsexs, sys.argv[2])
    #checkPkl(sys.argv[1])