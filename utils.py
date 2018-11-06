import gen.TrackstreamEx_pb2 as ts
import os
from progressbar import ProgressBar
from sklearn.cluster import DBSCAN
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
        [track_id, measurement_type, central_freq_hz, bandwitdh_hz, average_azimut_deg]
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

    fig, ax = plt.subplots(len(args),sharex=True)
    for i in range(len(args)):

        key_indice = 1
        y_labels = []
        y_ticks = []
        for key in all_alternates["prp{}".format(i+1)]:
            boxes = []
            for alternate in all_alternates["prp{}".format(i+1)][key]:
                boxes.append((alternate.start.date_ms/(1000), alternate.duration_us/1000000))
            ax[i].broken_barh(boxes,(key_indice, 0.9), facecolors='blue')
            y_ticks.append(key_indice)
            y_labels.append(str(key))
            key_indice += 1
        ax[i].set_yticks(y_ticks)
        ax[i].set_yticklabels(y_labels)
        ax[i].set_ylabel("Id")
        ax[i].set_xlabel("Seconds")
    plt.show()

"""This part runs if you run 'python utils.py' in the console"""
if __name__ == '__main__':
    prp_1 = "prod/s1/TRC6420_ITRProduction_20181026_143235.prp"
    prp_2 = "prod/s2/TRC6420_ITRProduction_20181026_143231.prp"
    prp_3 = "prod/s3/TRC6420_ITRProduction_20181026_143233.prp"

    tsexs = get_track_stream_exs_from_prp(prp_1)
    raw_tracks = []

    for tsex in tsexs:
        raw_tracks = get_track_stream_ex_info(tsex, raw_tracks)

    y_pred, ids = get_dbscan_prediction(raw_tracks)

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
        ax.plot(corresponding_batches[key][:, 2], corresponding_batches[key][:, 1],
                corresponding_batches[key][:, 4], '-o', color=colors[key])

    plt.show() 
 