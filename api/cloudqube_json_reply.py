from qgis.PyQt.QtCore import QByteArray
from qgis.PyQt.QtNetwork import QNetworkReply

import json


class CloudqubeJsonReply:
    def __init__(self, reply, stream, callback, finished, error):
        reply.error.connect(error)
        reply.readyRead.connect(self.read)
        reply.finished.connect(self.finished)
        self._reply = reply
        self._callback = callback
        self._finished = finished
        self._data = QByteArray()
        # Storing request data stream so that it doesn't get
        # destroyed before sending it
        self._stream = stream

    def read(self):
        self._data.append(self._reply.readAll())

    def finished(self):
        if (self._reply.error() == QNetworkReply.NoError):
            self._data.append(self._reply.readAll())
            data_str = self._data.data().decode('utf-8')
            if len(data_str) > 0:
                self._callback(json.loads(data_str))
            else:
                self._callback()
            self._finished(self)
