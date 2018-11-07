import gen.TrackstreamEx_pb2 as ts
import os

from progressbar import ProgressBar
from sklearn.cluster import DBSCAN

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D


def read_prp(filepath):
    """Reads a .prp file, frame after frame, and returns an array of frames

    :param filepath: path to the .prp file to read
    :return: the list of all frames in the .prp file
    """
    print("\nReading .prp file from path %s" % filepath)
    frames = []
    with open(filepath, "rb") as f:
        file_size = os.path.getsize(filepath)
        progress = 0
        pbar = ProgressBar(maxval=file_size)
        pbar.start()
        while(file_size > progress):
            header_bytes = f.read(4)
            next_bytes = f.read(8)
            identification_bytes = f.read(4)

            data_type_bytes = f.read(2)
            data_type = int.from_bytes(data_type_bytes, byteorder='little')

            size_bytes = f.read(4)
            size = int.from_bytes(size_bytes, byteorder='little')

            track_stream_bytes = f.read(size)
            footer_bytes = f.read(4)
            ending_bytes = f.read(4)

            frame = {
                'header': header_bytes,
                'next': next_bytes,
                'identification': identification_bytes,
                'data_type': data_type,
                'size': size,
                'data': track_stream_bytes,
                'footer': footer_bytes,
                'ending': ending_bytes
            }
            frames.append(frame)

            frame_size = 4+8+4+2+4+size+4+4
            progress += frame_size
            pbar.update(progress)
        pbar.finish()
    print("Done ! Found %s frames in the file.\n" % len(frames))
    return(frames)


def get_track_stream_exs_from_prp(filepath):
    """Reads a .prp file, and takes TrackStreamEx objects from it

    :param filepath: path to the .prp file to read
    :return: the list of all TrackStreamEx objects in the .prp file
    """
    frames = read_prp(filepath)
    track_stream_exs = []
    for frame in frames:
        if frame['data_type'] == 518:
            TSEX = ts.TrackStreamEx()
            TSEX.ParseFromString(frame['data'])
            track_stream_exs.append(TSEX)
    return(track_stream_exs)


def get_track_info(track):
    """ Takes essential information out of a given track

    :param track: the track from which info should be extracted
    :return: a list containing the basic info of the track :
        [track_id, measurement_type, central_freq_hz,
            bandwitdh_hz, average_azimut_deg]
    """
    info_from_track = []
    info_from_track.append(track.itr_measurement.type)
    info_from_track.append(track.itr_measurement.central_freq_hz)
    info_from_track.append(track.itr_measurement.bandwidth_hz)
    info_from_track.append(track.average_azimut_deg)
    return info_from_track


def get_track_stream_ex_info(track_stream_ex, data=[]):
    """ Takes essential information out of a given TrackStreamEx object

    :param track_stream_ex: the TrackStreamEx object from which info should be extracted
    :param data: (optional) the data from other TrackStreamEx objects, that needs to be updated with new info
    :return: a list containing the basic info of every track contained in the TrackStreamEx object.
    """
    tracks = track_stream_ex.data.tracks
    for track in tracks:
        batch = get_track_info(track)
        if batch not in data:
            data.append(batch)
    return data


def get_track_list_info(tracks, data=[]):
    """ Takes essential information out of a given list of tracks

    :param tracks: the list of tracks from which info should be extracted
    :param data: (optional) the data from other track lists, that needs to be updated with new info
    :return: a list containing the basic info of every track contained in the input list.
    """
    for track in tracks:
        batch = get_track_info(track)
        if batch not in data:
            data.append(batch)
    return data


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


def display_alternates(*args):
    """ Function that displays all the alternates detected by a station

    :args: the prp files from all the stations
    """
    prps = [get_track_stream_exs_from_prp(args[i]) for i in range(len(args))]
    all_alternates = {}
    for i in range(len(prps)):
        all_alternates_current_prp = {}
        for tsex in prps[i]:
            if tsex.data.tracks:
                for track in tsex.data.tracks:
                    key_id = track.id.most_significant
                    all_alternates_current_prp[key_id] = track.alternates
                    """ if key_id in all_alternates_current_prp:
                        all_alternates_current_prp[key_id].append(current_alternate)
                    else:
                        all_alternates_current_prp[key_id] = [current_alternate] """
        all_alternates["prp{}".format(i + 1)] = all_alternates_current_prp

    fig, ax = plt.subplots(len(args), sharex=True)
    for i in range(len(args)):

        key_indice = 1
        y_labels = []
        y_ticks = []
        for key in all_alternates["prp{}".format(i+1)]:
            boxes = []
            for alternate in all_alternates["prp{}".format(i+1)][key]:
                boxes.append((alternate.start.date_ms/(1000),
                              alternate.duration_us/1000000))
            ax[i].broken_barh(boxes, (key_indice, 0.9), facecolors='blue')
            y_ticks.append(key_indice)
            y_labels.append(str(key))
            key_indice += 1
        ax[i].set_yticks(y_ticks)
        ax[i].set_yticklabels(y_labels)
        ax[i].set_ylabel("Id")
        ax[i].set_xlabel("Seconds")
    plt.show()


def same_emittor(track_1, track_2):
    """ This function lets you know if two given tracks come from the same emitter.

    :param track_1: The first track
    :param track_2: The second track
    :return: A boolean, True if both tracks are from the same emitter, False if not
    """
    alternate_consistency = False

    # First of all, check if both tracks use the same frequence to communicate
    freq_consistency = False
    f_1 = track_1.itr_measurement.central_freq_hz
    f_2 = track_2.itr_measurement.central_freq_hz
    if f_1 > 0.99*f_2 and f_1 < 1.01*f_2:
        freq_consistency = True

    # Then, check if the bandwidth of both tracks is the same
    bandwidth_consistency = False
    bw_1 = track_1.itr_measurement.bandwidth_hz
    bw_2 = track_2.itr_measurement.bandwidth_hz
    if bw_1 > 0.99*bw_2 and bw_1 < 1.01*bw_2:
        bandwidth_consistency = True

    # Is the emission type the same for both tracks ?
    type_consistency = False
    t_1 = track_1.itr_measurement.type
    t_2 = track_2.itr_measurement.type
    if t_1 == t_2:
        type_consistency = True

    # If all three criteria above have been fulfilled, check if alternates sequences are similar
    if freq_consistency and type_consistency and bandwidth_consistency:
        """print(
            "\tFreq and type consistency found : \n\t\t1° Freq - %s - Type - %s \n\t\t2° Freq - %s - Type - %s" % (f_1, t_1, f_2, t_2))"""

        alternate_consistency = True
        alternates_1 = track_1.alternates
        alternates_2 = track_2.alternates

        alt_duration_1 = [alt.duration_us for alt in alternates_1]
        alt_start_1 = [alt.start.date_ms for alt in alternates_1]
        alt_duration_2 = [alt.duration_us for alt in alternates_2]
        alt_start_2 = [alt.start.date_ms for alt in alternates_2]

        # Both tracks may not have been recorded at exactly the same time. Therefore,
        # we only analyse alternates that have finished. Not ongoing alternates.
        n = (len(alternates_1) if len(alternates_1) < len(
            alternates_2) else len(alternates_2)) - 1

        for k in range(1, n):
            # If there is more than a single alternate, we check if the duration of the alternates is consistent
            if n > 0 and alt_duration_1[k] != alt_duration_2[k]:
                alternate_consistency = False
                break
            # Always check that the start-dates of all alternates are the same.
            if alt_start_1[k] != alt_start_2[k]:
                alternate_consistency = False
                break

        if alternate_consistency:
            """print(
                "\tBoth tracks are from the same emitter ! \n\t\tAnalysis made on %s alternates." % n)"""

    return freq_consistency and bandwidth_consistency and type_consistency and alternate_consistency


def sync_station_streams(station_1_track_stream, station_2_track_stream):
    """ Syncs track_streams between stations, to have them start at the same time.

    :param station_1_track_stream: track stream for first station
    :param station_2_track_stream: track stream for second station
    """
    s_1_dates = [station_1_track_stream[i].data.debut_cycle.date_ms for i in range(
        len(station_1_track_stream))]
    s_2_dates = [station_2_track_stream[i].data.debut_cycle.date_ms for i in range(
        len(station_2_track_stream))]
    min_cycle_duration = min(
        station_1_track_stream[0].data.duree_cycle_ms, station_2_track_stream[0].data.duree_cycle_ms)

    while s_1_dates[0] - s_2_dates[0] > min_cycle_duration:
        s_2_dates.pop(0)
        station_2_track_stream.pop(0)

    while s_2_dates[0] - s_1_dates[0] > min_cycle_duration:
        s_1_dates.pop(0)
        station_1_track_stream.pop(0)

    if s_2_dates[0] - s_1_dates[0] > min_cycle_duration/2:
        s_1_dates.pop(0)
        station_1_track_stream.pop(0)
    elif s_1_dates[0] - s_2_dates[0] > min_cycle_duration/2:
        s_2_dates.pop(0)
        station_2_track_stream.pop(0)


def sync_stations(*args):
    """Syncs all station streams passed as inputs.
    """
    n = len(args)
    args = list(args)
    if n < 2:
        raise ValueError(
            "Need at least 2 stations to sync, but was given only %s" % n)
    args.sort(key=len)

    for i in range(n-1):
        sync_station_streams(args[i], args[i+1])


def get_fused_station_tracks(station_1_track_streams, station_2_track_streams):
    global_track_streams = []
    n = min(len(station_1_track_streams), len(station_2_track_streams))
    progress = 0
    pbar = ProgressBar(maxval=n)
    pbar.start()
    for i in range(n):
        track_stream_1 = station_1_track_streams[i].data.tracks
        track_stream_2 = station_2_track_streams[i].data.tracks

        track_stream = [track for track in track_stream_1]

        for track_2 in track_stream_2:
            is_in_other = False
            for track_1 in track_stream_1:
                if same_emittor(track_1, track_2):
                    is_in_other = True
            if not is_in_other:
                track_stream.append(track_2)

        global_track_streams.append(track_stream)
        progress += 1
        pbar.update(progress)
    pbar.finish()
    return(global_track_streams)


def fuse_all_station_tracks(*args):
    """Fuse all station streams passed as inputs and returns the output.
    """
    n = len(args)
    args = list(args)
    if n < 2:
        raise ValueError(
            "Need at least 2 stations to fuse, but was given only %s" % n)

    global_track_streams = args[0]
    for i in range(n-1):
        global_track_streams = get_fused_station_tracks(
            global_track_streams, args[i+1])


"""This part runs if you run 'python utils.py' in the console"""
if __name__ == '__main__':
    #prp_1 = "prod/station1.prp"
    #prp_2 = "prod/station2.prp"
    prp_1 = "prod/s1/TRC6420_ITRProduction_20181026_143235.prp"
    prp_2 = "prod/s2/TRC6420_ITRProduction_20181026_143231.prp"
    prp_3 = "prod/s3/TRC6420_ITRProduction_20181026_143233.prp"

    tsexs_1 = get_track_stream_exs_from_prp(prp_1)
    tsexs_2 = get_track_stream_exs_from_prp(prp_2)
    # tsexs_3 = get_track_stream_exs_from_prp(prp_3)

    sync_stations(tsexs_1, tsexs_2)
    print("FUSING SHIT")
    global_track_streams = get_fused_station_tracks(tsexs_1, tsexs_2)
    print("DONE")
    stations_data = []
    raw_tracks = []

    for tracks in global_track_streams:
        raw_tracks = get_track_list_info(tracks, raw_tracks)

    print(len(raw_tracks))
    input()

    y_pred, ids = get_dbscan_prediction(raw_tracks)
    """

    stations_data = []
    for tsexs in [tsexs_1, tsexs_2]:
        raw_tracks = []
        real_tracks = []
        for tsex in tsexs:
            raw_tracks = get_track_stream_ex_info(tsex, raw_tracks)
            real_tracks.append(tsex.data.tracks)
        print(len(real_tracks))
        y_pred, ids = get_dbscan_prediction(raw_tracks)
        stations_data.append([y_pred, ids, real_tracks])
    stations_data = np.array(stations_data)

    y_pred, ids = get_dbscan_prediction(raw_tracks)

    """
    """df = pd.concat([pd.DataFrame({'ID': stations_data[i, 1], 'LABEL': stations_data[i, 0]})
                    for i in range(2)], keys=['Station 1', 'Station 2'])

    dup_df = df[df.duplicated(['ID'], keep=False)].sort_values(by="ID")
    print(dup_df)

    display_alternates(prp_1, prp_2)

    for cycle in range(100):
        for j in range(len(stations_data[0, 2][cycle])):
            scores = []
            for i in range(len(stations_data[1, 2][cycle])):
                comp = same_emittor(
                    stations_data[0, 2][cycle][j], stations_data[1, 2][cycle][i])
                scores.append(comp)

            tracks = np.where(scores)
            print(scores)
            print(j, tracks)
            print()

    """

    labels = []
    corresponding_batches = {}
    i = 0
    for label in y_pred:
        if label not in labels:
            labels.append(label)
            corresponding_batches[label] = []
        corresponding_batches[label].append(raw_tracks[i])
        i += 1

    fig = plt.figure()
    ax = Axes3D(fig)
    colors = cm.rainbow(np.linspace(0, 1, len(y_pred)))
    print("\nResult of DBScan clustering on input data. There are %s inputs and %s clusters.\n" %
          (len(raw_tracks), len(labels)))
    for key in corresponding_batches.keys():
        print("Label is %s" % key)
        for batch in corresponding_batches[key]:
            print("\tTrack data: % s" % batch)
        corresponding_batches[key] = np.array(corresponding_batches[key])
        ax.plot(corresponding_batches[key][:, 1], corresponding_batches[key][:, 0],
                corresponding_batches[key][:, 3], '-o', color=colors[key])

    plt.show()
