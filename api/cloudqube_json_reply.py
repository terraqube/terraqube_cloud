from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtNetwork import QNetworkReply
from qgis.core import QgsMessageLog
from .cloudqube_reply import CloudqubeReply

import json


class CloudqubeJsonReply(CloudqubeReply):
    def __init__(self, reply, stream, callback, finished, error):
        super().__init__(reply, error)
        #reply.readyRead.connect(self.read)
        reply.finished.connect(self.finished)
        reply.setReadBufferSize(1024*1024)
        self._callback = callback
        self._finished = finished
        self._data = QByteArray()
        # Storing request data stream so that it doesn't get
        # destroyed before sending it
        self._stream = stream

    def read(self):
        bytes_available = self._reply.bytesAvailable()
        data = self._reply.read(bytes_available)
        self._data.append(data)

    def finished(self):
        err = self._reply.error()
        if (err == QNetworkReply.NoError):
            self._data.append(self._reply.readAll())
            data_str = self._data.data().decode('utf-8')
            if len(data_str) > 0:
                self._callback(json.loads(data_str))
            else:
                self._callback()
            self._finished(self)
        else:
            QgsMessageLog.logMessage('Error {0}: {1}!'.format(err, self._reply.errorString()))

