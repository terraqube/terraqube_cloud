import tempfile

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest


class CloudqubeProgressReply:
    """Class that handles uploads with progress."""

    def __init__(self, reply, progress, callback, finished, error):
        reply.error.connect(error)
        reply.finished.connect(self.finished)
        reply.uploadProgress.connect(progress)
        self._reply = reply
        self._callback = callback
        self._finished = finished

    def finished(self):
        """Handles finished signal."""
        if (self._reply.error() == QNetworkReply.NoError):
            self._callback()
        # Call finished callback to remove this reply
        # which will remove all handling objects
        # and close all streams
        self._finished(self)

    def abort(self):
        self._reply.abort()
        