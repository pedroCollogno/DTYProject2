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
    info_from_track.append(track.id.most_significant)
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


def get_dbscan_prediction(data):
    """ Function that clusters data from TrackStreamEx objects

    :param data: The data to cluster using the dbscan algorithm
    :return: a tuple, in which there is :
        - in first position the array of predictions for all tracks given in entry
        - in second position an array containing the IDs of the predicted tracks.
    """
    np_data = np.array(data)
    prediction = DBSCAN(min_samples=1).fit_predict(np_data[:, 1:3])
    return prediction, np_data[:, 0]


def same_emittor(track_1, track_2):
    activity_consistency = False
    ca_1 = track_1.cumulated_activity_us
    ca_2 = track_2.cumulated_activity_us

    if ca_1 > 0.95*ca_2 and ca_1 < 1.05*ca_2:
        activity_consistency = True

    freq_consistency = False
    type_consistency = False

    if activity_consistency:
        alternate_consistency = True
        alternates_1 = track_1.alternates
        alternates_2 = track_2.alternates
        alt_duration_1 = [alt.duration_us for alt in alternates_1]
        alt_duration_2 = [alt.duration_us for alt in alternates_2]
        if len(alternates_1) == len(alternates_2):
            for i in range(len(alt_duration_1)):
                if alt_duration_1[i] != alt_duration_2[i]:
                    alternate_consistency = False
                    break
            if not alternate_consistency:
                alternate_consistency = True
                for i in range(len(alt_duration_1)-1):
                    if alt_duration_1[i] != alt_duration_2[i+1]:
                        alternate_consistency = False
                        break

            if not alternate_consistency:
                alternate_consistency = True
                for i in range(1, len(alt_duration_1)):
                    if alt_duration_1[i] != alt_duration_2[i-1]:
                        alternate_consistency = False
                        break
        else:
            alternate_consistency = False

    return activity_consistency  # and alternate_consistency


"""This part runs if you run 'python utils.py' in the console"""
if __name__ == '__main__':
    prp_1 = "prod/s1/TRC6420_ITRProduction_20181026_143235.prp"
    prp_2 = "prod/s2/TRC6420_ITRProduction_20181026_143231.prp"
    prp_3 = "prod/s3/TRC6420_ITRProduction_20181026_143233.prp"

    tsexs_1 = get_track_stream_exs_from_prp(prp_1)
    tsexs_2 = get_track_stream_exs_from_prp(prp_2)
    tsexs_3 = get_track_stream_exs_from_prp(prp_3)

    stations_data = []
    for tsexs in [tsexs_1, tsexs_2, tsexs_3]:
        raw_tracks = []
        real_tracks = []
        for tsex in tsexs:
            raw_tracks = get_track_stream_ex_info(tsex, raw_tracks)
            real_tracks.append(tsex.data.tracks)
        print(len(real_tracks))
        y_pred, ids = get_dbscan_prediction(raw_tracks)
        stations_data.append([y_pred, ids, real_tracks])
    stations_data = np.array(stations_data)
    df = pd.concat([pd.DataFrame({'ID': stations_data[i, 1], 'LABEL': stations_data[i, 0]})
                    for i in range(3)], keys=['Station 1', 'Station 2', 'Station 3'])

    dup_df = df[df.duplicated(['ID'], keep=False)].sort_values(by="ID")
    print(dup_df)

    for j in range(len(stations_data[0, 2][40])):
        scores = []
        for i in range(len(stations_data[1, 2][40])):
            comp = same_emittor(
                stations_data[0, 2][40][j], stations_data[1, 2][40][i])
            scores.append(comp)

        tracks = np.where(scores)
        print()
        print(j, tracks)

    """labels = []
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
            ax.plot(corresponding_batches[key][:, 2], corresponding_batches[key][:, 1],
                    corresponding_batches[key][:, 4], '-o', color=colors[key])

        plt.show()"""
