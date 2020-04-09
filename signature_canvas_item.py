from qgis.core import QgsMessageLog, Qgis
from qgis.gui import QgsMapCanvasItem
from qgis.PyQt.QtGui import QImage


class SignatureCanvasItem(QgsMapCanvasItem):
    def __init__(self, canvas, filename, point):
        super().__init__(canvas)
        self._canvas = canvas
        self._filename = filename
        self._location = point
        self._image = QImage(self._filename)


    def paint(self, painter, option, widget):
        point = self._canvas.getCoordinateTransform().transform(self._location)
        painter.drawImage(point.toQPointF(), self._image)
