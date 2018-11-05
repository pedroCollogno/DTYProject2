import gen.TrackstreamEx_pb2 as ts
import os
from progressbar import ProgressBar
from sklearn.cluster import DBSCAN
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.mplot3d import Axes3D

prp_1 = "prod/s1/TRC6420_ITRProduction_20181026_143235.prp"


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


def get_track_stream_ex(filepath):
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


tsexs = get_track_stream_ex(prp_1)
tsex = tsexs[38]
raw_data = []

for tsex in tsexs:
    track_stream_data = tsex.data
    tracks = track_stream_data.tracks
    print("Found %s tracks in the file.\n" % len(tracks))

    for track in tracks:
        batch = []
        batch.append(track.itr_measurement.type)
        batch.append(track.itr_measurement.central_freq_hz)
        batch.append(track.itr_measurement.bandwidth_hz)
        batch.append(track.average_azimut_deg)

        # batch.append(track.begin_date.date_ms)
        # batch.append(track.end_date.date_ms)
        if batch not in raw_data:
            raw_data.append(batch)
    """for batch in raw_data:
        print("Track data :", batch)"""
raw_data = np.array(raw_data)
y_pred = DBSCAN(min_samples=1).fit_predict(raw_data[:, :3])

labels = []
corresponding_batches = {}
i = 0
for label in y_pred:
    if label not in labels:
        labels.append(label)
        corresponding_batches[label] = []
    corresponding_batches[label].append(raw_data[i])
    i += 1

fig = plt.figure()
ax = Axes3D(fig)
colors = cm.rainbow(np.linspace(0, 1, len(y_pred)))
print("\nResult of DBScan clustering on input data. There are %s inputs and %s clusters.\n" %
      (len(raw_data), len(labels)))
for key in corresponding_batches.keys():
    print("Label is %s" % key)
    for batch in corresponding_batches[key]:
        print("\tTrack data: % s" % batch)
    corresponding_batches[key] = np.array(corresponding_batches[key])
    ax.plot(corresponding_batches[key][:, 1], corresponding_batches[key][:, 0],
            corresponding_batches[key][:, 3], '-o', color=colors[key])

plt.show()
