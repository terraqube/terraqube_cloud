from .cloudqube_progress_reply import CloudqubeProgressReply
from qgis.core import QgsMessageLog

class CloudqubeMultipartProgressReply(CloudqubeProgressReply):
    """Class that handles progress of multipart uploads."""

    def __init__(self, bytes_read, total_size, reply, progress, callback, finished, error):
        super().__init__(reply, self.total_progress, callback, finished, error)
        self._bytes_read = bytes_read
        self._total_size = total_size
        self._progress = progress

    def total_progress(self, bytes_read, total_bytes):
        if bytes_read > 0:
            self._progress(self._bytes_read + bytes_read, self._total_size)    

