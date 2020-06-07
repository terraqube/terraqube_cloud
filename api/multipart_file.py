from qgis.PyQt.QtCore import QFile
from qgis.core import QgsMessageLog, Qgis


class MultipartFile(QFile):
    """Wrapper class to support reading a file in chunks and post each part separately."""
    def __init__(self, filename):
        super().__init__(filename)
        self._file = QFile(filename)
        self._bytes_left = 0
        self._file.readyRead.connect(self.on_readyRead)
        self._file.aboutToClose.connect(self.on_aboutToClose)
        self._file.bytesWritten.connect(self.on_bytesWritten)
        self._file.channelBytesWritten.connect(self.on_channelBytesWritten)
        self._file.channelReadyRead.connect(self.on_channelReadyRead)
        self._file.readChannelFinished.connect(self.on_readChannelFinished)

    def set_part_size(self, size):
        self._bytes_left = size
        self._original_size = size

    def commitTransaction(self):
        QgsMessageLog.logMessage('commitTransaction')
        return self._file.commitTransaction()

    def currentReadChannel(self):
        QgsMessageLog.logMessage('currentReadChannel')
        return self._file.currentReadChannel()

    def currentWriteChannel(self):
        QgsMessageLog.logMessage('currentWriteChannel')
        return self._file.currentWriteChannel()

    def errorString(self):
        QgsMessageLog.logMessage('errorString')
        return self._file.errorString()
    
    def getChar(self):
        if self._bytes_left > 0:
            QgsMessageLog.logMessage('getChar')
            self._bytes_left = self._bytes_left - 1
            return self._file.getChar()
        else:
            QgsMessageLog.logMessage('getChar(no bytes left)')
            return None

    def isOpen(self):
        QgsMessageLog.logMessage('isOpen')
        return self._file.isOpen()

    def isReadable(self):
        QgsMessageLog.logMessage('isReadable')
        return self._file.isReadable()

    def isTextModeEnabled(self):
        QgsMessageLog.logMessage('isTextModeEnabled')
        return self._file.isTextModeEnabled()

    def isTransactionStarted(self):
        QgsMessageLog.logMessage('isTransactionStarted')
        return self._file.isTransactionStarted()

    def isWritable(self):
        QgsMessageLog.logMessage('isWritable')
        return self._file.isWritable()

    def openMode(self):
        QgsMessageLog.logMessage('openMode')
        return self._file.openMode()

    def peek(self, maxlen):
        QgsMessageLog.logMessage('peek {0} {1}'.format(maxlen, self._bytes_left))
        if maxlen > self._bytes_left:
            maxlen = self._bytes_left
        return self._file.peek(maxlen)

    def read(self, max_size):
        QgsMessageLog.logMessage('read {0}'.format(max_size))
        return self._file.read(max_size)

    def readAll(self):
        QgsMessageLog.logMessage('readAll')
        data = self._file.read(self._bytes_left)
        self._bytes_left = self._bytes_left - len(data)
        return data

    def readChannelCount(self):
        QgsMessageLog.logMessage('readChannelCount')
        return self._file.readChannelCount()

    def readLine(self):
        QgsMessageLog.logMessage('readLine')
        return None

    def rollbackTransaction(self):
        QgsMessageLog.logMessage('rollbackTransaction')
        return self._file.rollbackTransaction()

    def setCurrentReadChannel(self, channel):
        QgsMessageLog.logMessage('setCurrentReadChannel {0}'.format(channel))
        return self._file.setCurrentReadChannel(channel)

    def setErrorString(self, errorString):
        QgsMessageLog.logMessage('setErrorString {0}'.format(errorString))
        return self._file.setErrorString(errorString)

    def setOpenMode(self, mode):
        QgsMessageLog.logMessage('setOpenMode {0}'.format(mode))
        return self._file.setOpenMode(mode)

    def setTextModeEnabled(self, enabled):
        QgsMessageLog.logMessage('setTextModeEnabled {0}'.format(enabled))
        return self._file.setTextModeenabled(enabled)

    def skip(self, maxSize):
        QgsMessageLog.logMessage('skip {0} {1}'.format(maxSize, self._bytes_left))
        if maxSize > self._bytes_left:
            maxSize = self._bytes_left
        return self._file.skip(maxSize)

    def startTransaction(self):
        QgsMessageLog.logMessage('startTransaction')
        return self._file.startTransaction()

    def ungetChar(self, c):
        QgsMessageLog.logMessage('ungetChar {0}'.format(c))
        return None

    def writeChannelCount(self):
        QgsMessageLog.logMessage('writeChannelCount')
        return self._file.writeChannelCount()

    def atEnd(self):
        QgsMessageLog.logMessage('atEnd')
        if self._bytes_left == 0:
            return True
        else:
            return self._file.atEnd()

    def bytesAvailable(self):
        QgsMessageLog.logMessage('bytesAvailable')
        real_bytes_available = self._file.bytesAvailable()
        if real_bytes_available > self._bytes_left:
            return self._bytes_left
        else:
            return real_bytes_available

    def bytesToWrite(self):
        QgsMessageLog.logMessage('bytesToWrite')
        return self._file.bytesToWrite()

    def canReadLine(self):
        QgsMessageLog.logMessage('canReadLine')
        return self._file.canReadLine()

    def close(self):
        QgsMessageLog.logMessage('close')
        return self._file.close()

    def isSequential(self):
        QgsMessageLog.logMessage('isSequential')
        return self._file.isSequential()

    def open(self, mode):
        QgsMessageLog.logMessage('open')
        return self._file.open(mode)

    def pos(self):
        QgsMessageLog.logMessage('pos')
        return self._original_size - self._bytes_left

    def readData(self, max_size):
        if max_size > self._bytes_left:
            max_size = self._bytes_left
        self._bytes_left = self._bytes_left - max_size
        if self._bytes_left == 0:
            self.readChannelFinished.emit()
        QgsMessageLog.logMessage('readData {0}'.format(max_size))
        return self._file.readData(max_size)

    def reset(self):
        QgsMessageLog.logMessage('readData')
        return True

    def seek(self, pos):
        QgsMessageLog.logMessage('seek {0}'.format(pos))
        return True

    def size(self):
        file_size = self._file.size()
        if file_size < self._bytes_left:
            QgsMessageLog.logMessage('size(file_size) {0}'.format(file_size))
            return file_size
        else:
            QgsMessageLog.logMessage('size(bytes_left) {0}'.format(self._bytes_left))
            return self._bytes_left
    
    def waitForReadyRead(self, msecs):
        QgsMessageLog.logMessage('waitForReadyRead {0}'.format(msecs))
        return self._file.waitForReadyRead(msecs)

    def on_aboutToClose(self):
        QgsMessageLog.logMessage('on_aboutToClose')
        self.aboutToClose.emit()
    
    def on_bytesWritten(self, bytes_written):
        QgsMessageLog.logMessage('on_bytesWritten {0}'.format(bytes_written))
        self.bytesWritten.emit(bytes_written)

    def on_channelBytesWritten(self, channel, bytes_written):
        QgsMessageLog.logMessage('on_channelBytesWritten {0} {1}'.format(channel, bytes_written))
        self.channelBytesWritten.emit(channel, bytes_written)
    
    def on_channelReadyRead(self, channel):
        QgsMessageLog.logMessage('on_channelReadyRead {0}'.format(channel))
        if self._bytes_left > 0:
            self.channelReadyRead.emit(channel)

    def on_readChannelFinished(self):
        QgsMessageLog.logMessage('on_readChannelFinished')
        self.readChannelFinished.emit()

    def on_readyRead(self):
        QgsMessageLog.logMessage('on_readyRead')
        if self._bytes_left > 0:
            self.readyRead.emit()

    def flush(self):
        QgsMessageLog.logMessage('flush')
        return self._file.flush()

    def fileName(self):
        QgsMessageLog.logMessage('filename')
        return self._file.fileName()

    def exists(self):
        QgsMessageLog.logMessage('exists')
        return self._file.exists()

    def decodeName(self, localFileName):
        QgsMessageLog.logMessage('decodeName {0}'.format(localFileName))
        return self._file.decodeName(localFileName)