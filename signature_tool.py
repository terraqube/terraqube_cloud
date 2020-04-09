from qgis.PyQt.QtCore import Qt
from qgis.gui import QgsMapTool
from math import floor

class SignatureTool(QgsMapTool): 
    def __init__(self, canvas, layer, hiperqube_id, callback):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.layer = layer
        self.hiperqube_id = hiperqube_id
        self.callback = callback
        self.parent().setCursor(Qt.CrossCursor)

    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton: 
            x = event.pos().x()
            y = event.pos().y()

            # clicked position on screen to map coordinates
            point = self.canvas.getCoordinateTransform().toMapCoordinates(x, y)
            data_provider = self.layer.dataProvider()
            extent = data_provider.extent() 
            width = data_provider.xSize() if data_provider.capabilities() & data_provider.Size else 1000 
            height = data_provider.ySize() if data_provider.capabilities() & data_provider.Size else 1000 
            xres = extent.width() / width 
            yres = extent.height() / height
            if extent.xMinimum() <= point.x() <= extent.xMaximum() and \
                extent.yMinimum() <= point.y() <= extent.yMaximum():
                col = int(floor((point.x() - extent.xMinimum()) / xres))
                row = int(floor((extent.yMaximum() - point.y()) / yres))

                self.canvas.unsetMapTool(self)
                self.callback(self.hiperqube_id, row, col)
