from gen import TrackstreamEx_pb2 as ts
from json2pb import json2pb

import json
import logging
logger = logging.getLogger('backend')


class TrackGen:

    def __init__(self):
        self.id = {
            "least_significant": 0,
            "most_significant": 0
        }
        self.itr_measurement = {
            "type": 1,
            "central_freq_hz": 0,
            "bandwidth_hz": 0,
            "rx_level_dbm": 0
        }
        self.alternates = []
        self.begin_date = {
            "date_ms": 0,
        }
        self.cumulated_activity_us = 0
        self.average_azimut_deg = 0
        self.new_track = True

        self.json_track = {
            'id': self.id,
            'itr_measurement': self.itr_measurement,
            'alternates': self.alternates,
            'begin_date': self.begin_date,
            'cumulated_activity_us': self.cumulated_activity_us,
            'average_azimut_deg': self.average_azimut_deg,
            'new_track': self.new_track,
            'DESCRIPTOR': ts.TrackData
        }

        track = ts.TrackData()

        self.track = json2pb(track, self.json_track)
        logger.warning(self.track)


if __name__ == "__main__":
    t_gen = TrackGen()
