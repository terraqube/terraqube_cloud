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
    