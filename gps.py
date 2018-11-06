import math as m


def coords_from_tracks(track_1, track_2):
    """ Gives you the coordinates of the point located at the intersection of tracks 1 and 2

    :param track_1: the first track
    :param track_2: the second track
    :return: a tuple containing (lat, lng) coordinates to the intersection
    """
    station_1_coords = (track_1.alternates[0].sensor_position.latitude_deg,
                        track_1.alternates[0].sensor_position.longitude_deg)
    station_2_coords = (track_2.alternates[0].sensor_position.latitude_deg,
                        track_2.alternates[0].sensor_position.longitude_deg)
    azimuth_1 = track_1.average_azimut_deg
    azimuth_2 = track_2.average_azimut_deg

    if station_1_coords == station_2_coords:
        raise ValueError(
            "Cannot determine position : both tracks were measured on the same station.")
    return coords_from_azimuts(azimuth_1, azimuth_2, station_1_coords, station_2_coords)


def coords_from_azimuts(azimuth_1, azimuth_2, station_1_coords, station_2_coords):
    """ Gives you the coordinates of the point you get by tracing azimuth_1 from station 1 and azimuth_2 from station 2

    :param azimuth_1: The angle from which you percieve an incoming signal in station 1
    :param azimuth_2: The angle from which you percieve an incoming signal in station 2
    :param station_1_coords: The (lat, lng) coordinates of station 1
    :param station_2_coords: The (lat, lng) coordinates of station 2

    :return: a tuple containing (lat, lng) coordinates of the emitter
    """
    t1 = 1 / m.tan(m.radians(azimuth_1))
    t2 = 1 / m.tan(m.radians(azimuth_2))
    x1, y1 = station_1_coords
    x2, y2 = station_2_coords

    x = (y1 - y2 + t2*x2 - t1*x1)/(t2 - t1)
    y = t1*x1 + y1
    return(x, y)
