from .track_utils import get_track_id, add_track_to_dict
from .gps import coords_from_tracks
from progressbar import ProgressBar
import logging
logger = logging.getLogger('backend')


def sync_stations(*args):
    """Syncs all station streams passed as inputs.
    """
    n = len(args)
    args = list(args)
    if n < 2:
        raise ValueError(
            "Need at least 2 stations to sync, but was given only %s" % n)
    args.sort(key=len, reverse=False)
    for i in range(n-1):
        sync_station_streams(args[i], args[i+1])


def sync_station_streams(station_1_track_stream, station_2_track_stream):
    """ Syncs track_streams between stations, to have them start at the same time.

    :param station_1_track_stream: track stream for first station
    :param station_2_track_stream: track stream for second station
    """
    s_1_dates = [station_1_track_stream[i].debut_cycle.date_ms for i in range(
        len(station_1_track_stream))]
    s_2_dates = [station_2_track_stream[i].debut_cycle.date_ms for i in range(
        len(station_2_track_stream))]
    min_cycle_duration = min(
        station_1_track_stream[0].duree_cycle_ms, station_2_track_stream[0].duree_cycle_ms)

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
    logger.info("Final dates for sync : %s - %s" %
                (s_1_dates[0], s_2_dates[0]))


def fuse_all_station_tracks(*args):
    """Fuse all station streams passed as inputs and returns the output.
    """
    n = len(args)
    args = list(args)
    if n < 2:
        raise ValueError(
            "Need at least 2 stations to fuse, but was given only %s" % n)

    global_track_streams = []
    met_track_ids = []
    all_tracks_data = {}
    for i in range(n-1):
        if i == 0:
            global_track_streams, all_tracks_data, met_track_ids = get_fused_station_tracks(
                args[i], args[i+1], all_track_data={})

        else:
            global_track_streams, all_tracks_data, met_track_ids = get_fused_station_tracks(
                global_track_streams, args[i+1], are_lists=[True, False], all_track_data=all_tracks_data, met_track_ids=met_track_ids)

    return global_track_streams, all_tracks_data


def get_fused_station_tracks(station_1_track_streams, station_2_track_streams, are_lists=[False, False], all_track_data={}, met_track_ids=[]):
    """Fuses the track stream for two given stations. Returns a track list, without duplicates

    :param station_1_track_streams: the track streams from the first station
    :param station_2_track_streams: the track streams from the second station
    :param are_lists: (optional) list of two booleans, to allow you to replace a TrackStream object
        by a list of tracks in input.
    """
    try:
        global_track_streams = []
        n = min(len(station_1_track_streams), len(station_2_track_streams))
        progress = 0
        pbar = ProgressBar(maxval=n)
        pbar.start()

        for i in range(n):
            if not are_lists[0]:
                track_stream_1 = station_1_track_streams[i].tracks
            else:
                track_stream_1 = station_1_track_streams[i]

            if not are_lists[1]:
                track_stream_2 = station_2_track_streams[i].tracks
            else:
                track_stream_2 = station_2_track_streams[i]

            track_stream = []
            for track in track_stream_1:
                track_id = get_track_id(track)
                if track_id not in all_track_data.keys():
                    add_track_to_dict(track, all_track_data)
                if track_id not in met_track_ids:
                    met_track_ids.append(track_id)
                track_stream.append(track)

            for track_2 in track_stream_2:
                track_2_id = get_track_id(track_2)

                for track_1 in track_stream:
                    track_1_id = get_track_id(track_1)

                    if track_2_id not in all_track_data.keys():
                        add_track_to_dict(
                            track_2, all_track_data)

                    if track_1_id == track_2_id:
                        lat, lng = coords_from_tracks(track_1, track_2)
                        all_track_data[track_2_id]['coordinates'] = {
                            'lat': lat,
                            'lng': lng
                        }

                if track_2_id not in met_track_ids:
                    met_track_ids.append(track_2_id)
                    track_stream.append(track_2)

            global_track_streams.append(track_stream)
            progress += 1
            pbar.update(progress)

        pbar.finish()

    except ValueError as e:
        logger.error("Ran into ValueError : %s \nWhen looking at track %s" % (
            e, track_2_id))

    return(global_track_streams, all_track_data, met_track_ids)


def get_station_coordinates(*args):
    """ Returns the coordinates of all stations from which the .prp files come from

    :return: a dict containing all stations from a simulation
    """
    station_coords = {}
    i = 1
    found_station = False
    for arg in args:
        for track_stream in arg:
            for track in track_stream.tracks:
                if len(track.alternates) > 0:
                    station_name = 'station' + str(i)
                    station_coords[station_name] = {}
                    station_coords[station_name]['coordinates'] = {
                        'lat': track.alternates[0].sensor_position.latitude_deg,
                        'lng': track.alternates[0].sensor_position.longitude_deg
                    }
                    found_station = True
                    break
            if found_station:
                found_station = False
                break
        i += 1
    return(station_coords)


def initiate_emittors_positions(*args):
    """ Returns the coordinates of all emittors at the very end of the simulation from the .prp files

    :return: a dict containing all emittors from a simulation
    """
    n = len(args[0])

    track_streams = []
    for arg in args:
        track_streams.append(arg)

    global_track_streams, all_tracks_data = fuse_all_station_tracks(
        *track_streams)
    logger.debug("Merge done !")

    return(all_tracks_data)
