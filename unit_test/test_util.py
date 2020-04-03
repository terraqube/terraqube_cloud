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
