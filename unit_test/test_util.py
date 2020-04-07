import unittest
import util


class TestUtil(unittest.TestCase):

    def test_get_filename_without_extension(self):
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.txt'), '/path/to/file/file.txt')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.txt.gz'), '/path/to/file/file.txt')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.txt.bil'), '/path/to/file/file.txt')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.txt.bil.gz'), '/path/to/file/file.txt')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.txt.gz.bil'), '/path/to/file/file.txt.gz')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file'), '/path/to/file/file')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.bil'), '/path/to/file/file')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.gz'), '/path/to/file/file')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.bil.gz'), '/path/to/file/file')
        self.assertEqual(util.get_filename_without_extension(
            '/path/to/file/file.gz.bil'), '/path/to/file/file.gz')

    def test_calculate_average_dist(self):
        self.assertIsNone(util.calculate_average_dist([]))
        self.assertIsNone(util.calculate_average_dist([ 0.0 ]))
        self.assertIsNone(util.calculate_average_dist([ 400.0 ]))
        self.assertEqual(util.calculate_average_dist([ 400.0, 400.5 ]), 0.5)
        self.assertEqual(util.calculate_average_dist([ 400.0, 400.5, 401 ]), 0.5)
        self.assertEqual(util.calculate_average_dist([ 400.0, 400.5, 401, 403 ]), 1.0)
        self.assertEqual(util.calculate_average_dist([ 400.0, 400.5, 401, 403, 404.0 ]), 1.0)

    def test_get_wavelength_stats(self):
        self.assertIsNone(util.get_wavelength_stats([]))
        self.assertEqual(util.get_wavelength_stats([ 0.0 ]), ( 0.0, 0.0, None ))
        self.assertEqual(util.get_wavelength_stats([ 400.0 ]), (400.0, 400.0, None ))
        self.assertEqual(util.get_wavelength_stats([ 400.0, 400.5 ]), (400.0, 400.5, 0.5))
        self.assertEqual(util.get_wavelength_stats([ 400.0, 400.5, 401 ]), (400.0, 401, 0.5))
        self.assertEqual(util.get_wavelength_stats([ 400.0, 400.5, 401, 403 ]), (400.0, 403, 1.0))
        self.assertEqual(util.get_wavelength_stats([ 400.0, 400.5, 401, 403, 404.0 ]), (400.0, 404.0, 1.0))
        