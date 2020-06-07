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
        QgsMessageLog.logMessage('Is text mode enabled: {0}'.format(reply.isTextModeEnabled()))
        reply.setReadBufferSize(1024*1024)
        QgsMessageLog.logMessage('Read buffer size: {0}'.format(reply.readBufferSize()))
        self._callback = callback
        self._finished = finished
        self._data = QByteArray()
        # Storing request data stream so that it doesn't get
        # destroyed before sending it
        self._stream = stream

    def read(self):
        QgsMessageLog.logMessage('Reading data')
        QgsMessageLog.logMessage('Headers: {0}'.format(self._reply.rawHeaderPairs()))
        bytes_available = self._reply.bytesAvailable()
        QgsMessageLog.logMessage('Bytes available: {0}'.format(bytes_available))
        data = self._reply.read(bytes_available)
        QgsMessageLog.logMessage('Data size: {0}'.format(len(data)))
        self._data.append(data)
        QgsMessageLog.logMessage('Data: {0}'.format(data))

    def finished(self):
        QgsMessageLog.logMessage('Finished')
        err = self._reply.error()
        if (err == QNetworkReply.NoError):
            QgsMessageLog.logMessage('No error')
            self._data.append(self._reply.readAll())
            data_str = self._data.data().decode('utf-8')
            if len(data_str) > 0:
                self._callback(json.loads(data_str))
            else:
                self._callback()
            self._finished(self)
        else:
            QgsMessageLog.logMessage('Error {0}: {1}!'.format(err, self._reply.errorString()))
        QgsMessageLog.logMessage('Exit finish')

