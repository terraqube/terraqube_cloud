from enum import Enum
from qgis.core import QgsMessageLog, Qgis, QgsPointXY
from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapTool, QgsRubberBand
from math import floor

class SignatureTool(QgsMapTool):
    """
        On Double click it will callback with an array with a single pixel.
        On Single click without releasing it will draw a square and callback
        the starting and ending point in an array.
        On Single click with releasing it will start drawing a polygon and
        every subsequent single click will add a new vertex in the polygon.
        On Right click it will callback with an array with all the vertex in
        the polygon.
        On Escape it will clean up the array and start over.
    """
    def __init__(self, canvas, layer, callback):
        QgsMapTool.__init__(self, canvas)
        self._canvas = canvas
        self._layer = layer
        self._callback = callback
        self._pixels = []
        self._start_point = None
        self._mode = Mode.NONE
        self._rubber_band = QgsRubberBand(self._canvas)
        self._rubber_band.setColor(Qt.red)
        self._rubber_band.setWidth(1)
        self.parent().setCursor(Qt.CrossCursor)

    def getPoint(self, pos):
        x = pos.x()
        y = pos.y()
        return self._canvas.getCoordinateTransform().toMapCoordinates(x, y)  
    
    def getRowCol(self, point):
        # clicked position on screen to map coordinates
        data_provider = self._layer.dataProvider()
        extent = data_provider.extent() 
        width = data_provider.xSize() if data_provider.capabilities() \
            & data_provider.Size else 1000 
        height = data_provider.ySize() if data_provider.capabilities() \
            & data_provider.Size else 1000 
        xres = extent.width() / width 
        yres = extent.height() / height
        if extent.xMinimum() <= point.x() <= extent.xMaximum() and \
            extent.yMinimum() <= point.y() <= extent.yMaximum():
            col = int(floor((point.x() - extent.xMinimum()) / xres))
            row = int(floor((extent.yMaximum() - point.y()) / yres))
            return (row, col)
        else:
            return None        

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self._pixels = []
            self.finish()

    def canvasMoveEvent(self, event):
        point = self.getPoint(event.pos())
        if self._mode is Mode.SQUARE:
            if not point.compare(self._start_point):
                self._rubber_band.reset()
                self._rubber_band.addPoint(self._start_point, False)
                self._rubber_band.addPoint(QgsPointXY(self._start_point.x(), point.y()), False)
                self._rubber_band.addPoint(point, False)
                self._rubber_band.addPoint(QgsPointXY(point.x(), self._start_point.y()), False)
                self._rubber_band.closePoints()
        elif self._mode is Mode.POLYGON:
            self._rubber_band.movePoint(self._rubber_band.numberOfVertices() - 1, point)

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.getPoint(event.pos())
            if self._mode is Mode.SQUARE:
                if self._start_point.compare(point):
                    self._mode = Mode.POLYGON
                    self._rubber_band.addPoint(point)
                    self._start_point = None
                else:
                    self._pixels = []
                    # The last vertex is repeated
                    for i in range(self._rubber_band.numberOfVertices() - 1):
                        self._pixels.append(self.getRowCol(self._rubber_band.getPoint(0, i)))
                    self.finish()
            elif self._mode is Mode.POLYGON:
                self._rubber_band.addPoint(point)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.getPoint(event.pos())
            pixel = self.getRowCol(point)
            if self._mode is Mode.NONE:
                self._mode = Mode.SQUARE
                self._start_point = QgsPointXY(point.x(), point.y())
            elif self._mode is Mode.POLYGON:
                self._rubber_band.removePoint(self._rubber_band.numberOfVertices() - 1)
            else:
                self._mode = Mode.POLYGON
            if pixel:
                self._rubber_band.addPoint(point)
                self._pixels.append(pixel)
        elif event.button() == Qt.RightButton:
            self.finish()

    def finish(self):
        self._canvas.unsetMapTool(self)
        self._rubber_band.reset()
        self._mode = Mode.NONE
        self._start_point = None
        if len(self._pixels) > 0:
            self._callback(self._layer.hiperqube_id(), self._pixels)


class Mode(Enum):
    NONE = 0
    SQUARE = 1
    POLYGON = 2
