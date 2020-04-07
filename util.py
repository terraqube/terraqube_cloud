import os.path
import requests
import zlib


def get_filename_without_extension(filename):
    """Returns the filename without extension."""
    res1, ext = os.path.splitext(filename.lower())
    if len(ext) > 0 and (ext == '.gz' or ext == '.bil'):
        res2, ext = os.path.splitext(res1)
        if len(ext) == 0 or ext == '.bil':
            return res2
        else:
            return res1
    else:
        return filename


def get_hdr_filename(filename):
    """Gets the appropriate HDR filename that matches the BIL file provided in filename."""
    return '{0}.hdr'.format(get_filename_without_extension(filename))


def calculate_average_dist(wavelengths):
    """Calculates the average distance between wavelenghts."""
    if len(wavelengths) > 1:
        dist = 0
        for i in range(1, len(wavelengths)):
            dist = dist + wavelengths[i] - wavelengths[i - 1]
        return dist / (len(wavelengths) - 1)
    else:
        return None


def get_wavelength_stats(wavelengths):
    """Gets the lowest wavelength value."""
    min_value = None
    max_value = None
    if len(wavelengths) > 0:
        min_value = wavelengths[0]
        max_value = wavelengths[len(wavelengths) - 1]
        avg_dist = calculate_average_dist(wavelengths)
        return (min_value, max_value, avg_dist)
    else:
        return None

def array_str_to_float(arr):
    return list(map(lambda elem: float(elem), arr))

"""Generator that reads a file in chunks and compresses them"""
def chunked_read_and_compress(file_to_send, zlib_obj, chunk_size):
    compression_incomplete = True
    with open(file_to_send,'rb') as f:
        # The zlib might not give us any data back, so we have nothing to yield, just
        # run another loop until we get data to yield.
        while compression_incomplete:
            plain_data = f.read(chunk_size)
            if plain_data:
                compressed_data = zlib_obj.compress(plain_data)
            else:
                compressed_data = zlib_obj.flush()
                compression_incomplete = False
            if compressed_data:
                yield compressed_data

"""Post a file to a url that is content-encoded gzipped compressed and chunked (for large files)"""
def post_file_gzipped(url, file_to_send, chunk_size=5*1024*1024, compress_level=6, headers={}, requests_kwargs={}):
    headers_to_send = {'Content-Encoding': 'gzip'}
    headers_to_send.update(headers)
    zlib_obj = zlib.compressobj(compress_level, zlib.DEFLATED, 31)
    return requests.post(url, data=chunked_read_and_compress(file_to_send, zlib_obj, chunk_size), headers=headers_to_send, **requests_kwargs)
