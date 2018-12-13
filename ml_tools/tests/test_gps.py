import unittest
from src.utils.gps import coords_from_azimuts


class TestGPSMethods(unittest.TestCase):

    def test_coords_from_azimuth(self):
        """
            Check that geolocalization works properly
        """

        point1 = (51.8853, 0.2545)
        point2 = (49.0034, 2.5735)

        azimuth_1 = 108.55
        azimuth_2 = 32.44

        target = (50.90760750047431, 4.508574645770475)

        result = coords_from_azimuts(
            azimuth_1, azimuth_2, point1, point2)

        self.assertEqual(result, target)


if __name__ == '__main__':
    unittest.main()
