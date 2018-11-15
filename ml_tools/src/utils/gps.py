""" This module is used to compute the location of emittors that are seen by stations
"""

from pygeodesy import sphericalNvector


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


def coords_from_azimuts(azimuth_1, azimuth_2, station_1_coords, station_2_coords, north_hem=True):
    """ Gives you the coordinates of the point you get by tracing azimuth_1 from station 1 and azimuth_2 from station 2

    :param azimuth_1: The angle from which you percieve an incoming signal in station 1
    :param azimuth_2: The angle from which you percieve an incoming signal in station 2
    :param station_1_coords: The (lat, lng) coordinates of station 1
    :param station_2_coords: The (lat, lng) coordinates of station 2

    :return: a tuple containing (lat, lng) coordinates of the emitter
    """
    point1 = sphericalNvector.LatLon(*station_1_coords)
    point2 = sphericalNvector.LatLon(*station_2_coords)
    point3 = sphericalNvector.triangulate(point1, azimuth_1, point2, azimuth_2)

    if point3.latlon[0] < 0 and north_hem:
        return(-point3.latlon[0], point3.latlon[1]-180)
    if point3.latlon[0] > 0 and not north_hem:
        return(-point3.latlon[0], 180-point3.latlon[1])

    return (point3.latlon[0], point3.latlon[1])
