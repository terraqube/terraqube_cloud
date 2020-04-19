import os.path
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
    """Gets the appropriate HDR filename that matches the BIL file provided in
    filename."""
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


def format_size(size, suffix='B'):
    """Formats the size of a hiperqube."""
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(size) < 1024.0:
            return "%3.1f%s%s" % (size, unit, suffix)
        size /= 1024.0
    return "%.1f%s%s" % (size, 'Yi', suffix)


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
