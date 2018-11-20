from .log import logger


def get_track_info(track):
    """ Takes essential information out of a given track

    :param track: the track from which info should be extracted
    :return: a list containing the basic info of the track :
        [measurement_type, central_freq_hz,
            bandwitdh_hz, average_azimut_deg, begin_date_ms, track_id]
    """
    info_from_track = []
    info_from_track.append(track.itr_measurement.type)
    info_from_track.append(track.itr_measurement.central_freq_hz)
    info_from_track.append(track.itr_measurement.bandwidth_hz)
    info_from_track.append(track.average_azimut_deg)
    info_from_track.append(track.begin_date.date_ms)
    info_from_track.append(get_track_id(info_from_track))
    return info_from_track


def get_track_stream_info(track_stream, data=[]):
    """ Takes essential information out of a given TrackStream object

    :param track_stream: the TrackStream object from which info should be extracted
    :param data: (optional) the data from other TrackStream objects, that needs to be updated with new info
    :return: a list containing the basic info of every track contained in the TrackStream object.
    """
    tracks = track_stream.tracks
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


def get_track_id(track):
    """Gets the unique ID from a track

    :param track: the track from which you wish to get the ID
    :return: the ID of the track, as an int
    """
    if type(track) is list:
        em_type = track[0]
        freq = track[1]
        track_begin_date = track[4]
    else:
        track_begin_date = track.begin_date.date_ms
        freq = track.itr_measurement.central_freq_hz
        em_type = track.itr_measurement.type

    track_begin_date = int(track_begin_date/100)*100
    freq = int(freq/100000)*100000

    track_id = track_begin_date*100**3 + freq * \
        100**2 + em_type*100**1

    return(track_id)


def same_emittor(track_1, track_2):
    """ This function lets you know if two given tracks come from the same emitter.

    :param track_1: The first track
    :param track_2: The second track
    :return: A boolean, True if both tracks are from the same emitter, False if not
    """
    alternate_consistency = False
    start_consistency = False
    start_1_index = 0
    start_2_index = 0

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
        # logger.debug(
        #    "\tFreq and type consistency found : \n\t\t1° Freq - %s - Type - %s \n\t\t2° Freq - %s - Type - %s" % (f_1, t_1, f_2, t_2))
        alternate_consistency = True
        alternates_1 = track_1.alternates
        alternates_2 = track_2.alternates

        alt_duration_1 = [alt.duration_us for alt in alternates_1]
        alt_start_1 = [alt.start.date_ms for alt in alternates_1]
        alt_duration_2 = [alt.duration_us for alt in alternates_2]
        alt_start_2 = [alt.start.date_ms for alt in alternates_2]

        # Both tracks may not have been recorded at exactly the same time. Therefore,
        # we only analyse alternates that have finished. Not ongoing alternates.
        n = min(len(alternates_1), len(alternates_2)) - 1

        for start_1 in alt_start_1:
            if start_1 in alt_start_2:
                start_1_index = alt_start_1.index(start_1)
                start_2_index = alt_start_2.index(start_1)
                start_consistency = True
                break
        if not start_consistency:
            for start_2 in alt_start_2:
                if start_2 in alt_start_1:
                    start_1_index = alt_start_1.index(start_2)
                    start_2_index = alt_start_2.index(start_2)
                    start_consistency = True
                    break

        if start_consistency and track_1.itr_measurement.type != 1:
            if start_1_index == 0 or start_2_index == 0:
                start_1_index += 1
                start_2_index += 1
            while start_1_index < len(alt_start_1) and start_2_index < len(alt_start_2):
                # If there is more than a single alternate, we check if the duration of the alternates is consistent
                if alt_duration_1[start_1_index] != alt_duration_2[start_2_index]:
                    alternate_consistency = False
                    break

                # Always check that the start-dates of all alternates are the same.
                if alt_start_1[start_1_index] != alt_start_2[start_2_index]:
                    alternate_consistency = False
                    break

                start_1_index += 1
                start_2_index += 1

        # if alternate_consistency:
        #    logger.debug(
        #        "\tBoth tracks are from the same emitter !")
    bool_response = freq_consistency and bandwidth_consistency and type_consistency and start_consistency and alternate_consistency

    track_id = get_track_id(track_1)
    return bool_response, track_id


def add_track_to_dict(track, track_dict, coords=None):
    """ Adds a track to a dictionnary of tracks in the right format

    :param track: the track to add to the dict
    :param track_dict: the dictionnary of tracks, to which the track data should be added
    :param coords: (optional) the gps coordinates of the emittor behind the track
    """
    track_id = get_track_id(track)
    freq = track.itr_measurement.central_freq_hz
    bandwidth = track.itr_measurement.bandwidth_hz
    em_type = track.itr_measurement.type
    track_info = get_track_info(track)

    track_data = {
        'track_id': track_id,
        'coordinates': coords,
        'frequency': freq,
        'emission_type': em_type,
        'network_id': None,
        'track': track_info
    }
    track_dict[track_id] = track_data
