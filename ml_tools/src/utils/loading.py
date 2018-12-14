import os
from .gen import TrackstreamEx_pb2 as ts

from progressbar import ProgressBar
import logging
logger = logging.getLogger('backend')


def read_prp(filepath):
    """Reads a .prp file, frame after frame, and returns an array of frames

    :param filepath: path to the .prp file to read
    :return: the list of all frames in the .prp file
    """
    logger.info("\nReading .prp file from path %s" % filepath)
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
    logger.info("Done ! Found %s frames in the file.\n" % len(frames))
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


def get_track_streams_from_prp(filepath):
    """Reads a .prp file, and takes TrackStream objects from it

    :param filepath: path to the .prp file to read
    :return: the list of all TrackStream objects in the .prp file
    """
    frames = read_prp(filepath)
    track_streams = []
    real_data = False
    for frame in frames:
        if frame['data_type'] == 512:
            real_data = True
            track_stream = ts.TrackStream()
            track_stream.ParseFromString(frame['data'])
            track_streams.append(track_stream)
        elif frame['data_type'] == 518:
            TSEX = ts.TrackStreamEx()
            TSEX.ParseFromString(frame['data'])
            track_streams.append(TSEX.data)

    return(track_streams)


def is_same_station_track(old_track, new_track):
    """ Lets you know if two tracks, taken on the same station at a different time, are from the same emitter

    :param old_track: a track from cycle number i
    :param new_track: a track from cycle number i+1
    """
    freq1 = int(old_track.itr_measurement.central_freq_hz/100000)
    em_type1 = old_track.itr_measurement.type

    freq2 = int(new_track.itr_measurement.central_freq_hz/100000)
    em_type2 = new_track.itr_measurement.type

    if freq1 == freq2 and em_type1 == em_type2:

        azim1 = old_track.average_azimut_deg
        azim_dev1 = old_track.standard_deviation_az_deg
        azim2 = new_track.average_azimut_deg
        azim_dev2 = new_track.standard_deviation_az_deg

        db1 = old_track.itr_measurement.rx_level_dbm
        db2 = new_track.itr_measurement.rx_level_dbm

        if azim2 < azim1 + 1+azim_dev1 and azim2 > azim1 - 1-azim_dev1:
            return True
        elif db2 > db1 - 2 and db2 < db1 + 2:
            return True

    return False
