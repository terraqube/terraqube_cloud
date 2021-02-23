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
        self._is_dragging = False
        self._start_point = None
        self._rubberBand = QgsRubberBand(self._canvas)
        self._rubberBand.setColor(Qt.red)
        self._rubberBand.setWidth(1)
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
        QgsMessageLog.logMessage("Key Release")
        if event.key() == Qt.Key_Escape:
            self._pixels = []
            self._rubberBand.reset()

    def canvasMoveEvent(self, event):
        if self._is_dragging:
            point = self.getPoint(event.pos())
            if not point.compare(self._start_point):
                QgsMessageLog.logMessage("{0} {1} {2} {3}".format(self._start_point.x(), self._start_point.y(), point.x(), point.y()))
                self._rubberBand.reset()
                self._rubberBand.addPoint(self._start_point, False)
                self._rubberBand.addPoint(QgsPointXY(self._start_point.x(), point.y()), False)
                self._rubberBand.addPoint(point, False)
                self._rubberBand.addPoint(QgsPointXY(point.x(), self._start_point.y()), False)
                self._pixels = []
                for i in range(self._rubberBand.size()):
                    self._pixels.append(self.getRowCol(self._rubberBand.getPoint(0, i)))
                self._rubberBand.closePoints()

    def canvasReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self._is_dragging:
                point = self.getPoint(event.pos())
                if not self._start_point.compare(point):
                    self.finish()
                self._is_dragging = False
                self._start_point = None

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            point = self.getPoint(event.pos())
            if self._rubberBand.size() == 0:
                self._is_dragging = True
                self._start_point = QgsPointXY(point.x(), point.y())
            self._rubberBand.addPoint(point)
            pixel = self.getRowCol(point)
            if pixel:
                self._pixels.append(pixel)
        elif event.button() == Qt.RightButton:
            self.finish()

    def finish(self):
        if len(self._pixels) > 0:
            self._canvas.unsetMapTool(self)
            self._rubberBand.reset()
            self._callback(self._layer.hiperqube_id(), self._pixels)
        