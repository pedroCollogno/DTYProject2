import unittest
from os.path import join, abspath, dirname
from src.utils import station_utils, loading


test_dir = abspath(dirname(__file__))


class TestStationUtils(unittest.TestCase):
    paths = [
        join(test_dir, 'res', 'station-1.prp'),
        join(test_dir, 'res', 'station-2.prp'),
        join(test_dir, 'res', 'station-3.prp')
    ]
    track_streams = []
    for path in paths:
        track_stream = loading.get_track_stream_exs_from_prp(path)
        track_streams.append(track_stream)

    def test_tracks_sync(self):
        """
            Check that track sync have worked properly
        """
        station_utils.sync_stations(*self.track_streams)

        all_dates = []
        for track_stream in self.track_streams:
            all_dates.append([track_stream[i].data.debut_cycle.date_ms for i in range(
                len(track_stream))])

        min_cycle_durations = [
            track_stream[0].data.duree_cycle_ms for track_stream in self.track_streams]
        min_cycle_duration = min(min_cycle_durations)

        for i in range(len(all_dates)):
            delta = abs(all_dates[i][0] - all_dates[i-1][0])
            self.assertTrue(delta <= min_cycle_duration)

    def test_station_coordinates(self):
        """
            Check that station coordinates response contains something for all stations
        """
        station_coords = station_utils.get_station_coordinates(
            *self.track_streams)

        self.assertIsInstance(station_coords, dict)
        for i in range(len(self.track_streams)):
            self.assertTrue('station'+str(i+1) in station_coords.keys())


if __name__ == '__main__':
    unittest.main()
