from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtWidgets import QTableWidgetItem


class SignatureTableWidgetItem(QTableWidgetItem):
    def __init__(self, signature, state, callback):
        QTableWidgetItem.__init__(self, '{0}, {1}'.format(
                str(signature['col']), str(signature['line'])))
        self.setCheckState(state)
        self._signature = signature
        self._callback = callback

    def signature(self):
        return self._signature
    
    def notify(self):
        active = True if self.checkState() == Qt.Checked else False
        self._callback(self._signature, active)
