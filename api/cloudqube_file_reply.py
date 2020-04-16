import tempfile

from qgis.PyQt.QtCore import QFile, QIODevice
from qgis.PyQt.QtNetwork import QNetworkReply, QNetworkRequest


class CloudqubeFileReply:
    """Class that handles file downloads."""

    def __init__(self, reply, callback, finished, error):
        reply.error.connect(error)
        reply.readyRead.connect(self.read)
        reply.finished.connect(self.finished)
        self._reply = reply
        self._callback = callback
        self._finished = finished

        # Figure out extension from content-type
        try:
            extension = '.{0}'.format(
                reply.header(QNetworkRequest.ContentTypeHeader).split('/')[1])
        except:
            extension = ''
        _, filename = tempfile.mkstemp(suffix=extension)
        
        self._filename = filename
        self._file = QFile(filename)
        self._file.open(QIODevice.WriteOnly)

    def read(self):
        """Handles read signal."""
        self._file.write(self._reply.readAll())

    def finished(self):
        """Handles finished signal."""
        if (self._reply.error() == QNetworkReply.NoError):
            # Write last remaining bytes if there are any
            self._file.write(self._reply.readAll())
            self._file.close()
            self._callback(self._filename)
            # Call finished callback to remove this reply
            # which will remove all handling objects
            # and close all streams
            self._finished(self)

    def filename(self):
        """Returns the name of the file that was downloaded."""
        return self._filename
