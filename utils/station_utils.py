import utils.gps as gps
from utils.track_utils import same_emittor

from progressbar import ProgressBar


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
    print("Final dates for sync : %s - %s" % (s_1_dates[0], s_2_dates[0]))


def fuse_all_station_tracks(*args):
    """Fuse all station streams passed as inputs and returns the output.
    """
    n = len(args)
    args = list(args)
    if n < 2:
        raise ValueError(
            "Need at least 2 stations to fuse, but was given only %s" % n)

    global_track_streams = []
    all_tracks_data = {}
    for i in range(n-1):
        if i == 0:
            global_track_streams, all_tracks_data = get_fused_station_tracks(
                args[i], args[i+1])
        else:
            global_track_streams, all_tracks_data = get_fused_station_tracks(
                global_track_streams, args[i+1], are_lists=[True, False], all_track_data=all_tracks_data)

    return global_track_streams, all_tracks_data


def get_fused_station_tracks(station_1_track_streams, station_2_track_streams, are_lists=[False, False], all_track_data={}):
    """Fuses the track stream for two given stations. Returns a track list, without duplicates

    :param station_1_track_streams: the track streams from the first station 
    :param station_2_track_streams: the track streams from the second station
    :param are_lists: (optional) list of two booleans, to allow you to replace a trackstreamex object 
        by a list of tracks in input.
    """

    global_track_streams = []
    n = min(len(station_1_track_streams), len(station_2_track_streams))
    progress = 0
    pbar = ProgressBar(maxval=n)
    pbar.start()
    for i in range(n):
        if not are_lists[0]:
            track_stream_1 = station_1_track_streams[i].data.tracks
        else:
            track_stream_1 = station_1_track_streams[i]

        if not are_lists[1]:
            track_stream_2 = station_2_track_streams[i].data.tracks
        else:
            track_stream_2 = station_2_track_streams[i]

        track_stream = [track for track in track_stream_1]
        previous_track_stream = []
        if i >= 1:
            previous_track_stream = global_track_streams[i-1]

        for track_2 in track_stream_2:
            is_in_other = False
            for track_1 in track_stream + previous_track_stream:
                is_same, track_2_id = same_emittor(track_2, track_1)
                if is_same:
                    is_in_other = True

                    if track_2_id not in all_track_data.keys():
                        lat, lng = gps.coords_from_tracks(track_1, track_2)
                        freq = track_1.itr_measurement.central_freq_hz
                        bandwidth = track_1.itr_measurement.bandwidth_hz
                        em_type = track_1.itr_measurement.type

                        track_data = {
                            'track_id': track_2_id,
                            'coordinates': {
                                'lat': lat,
                                'lng': lng
                            },
                            'network_id': None
                        }

                        all_track_data[track_2_id] = track_data
                    break

            if not is_in_other and len(track_stream) > 0:
                track_stream.append(track_2)

        global_track_streams.append(track_stream)
        progress += 1
        pbar.update(progress)
    pbar.finish()
    return(global_track_streams, all_track_data)