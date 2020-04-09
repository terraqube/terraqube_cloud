from qgis.PyQt.QtCore import QPoint
from qgis.core import QgsMessageLog, Qgis, QgsRasterLayer, QgsProject, QgsPointXY
from qgis.gui import QgsVertexMarker
from .signature_canvas_item import SignatureCanvasItem

MARKERS_KEY = 'markers'

class HiperqubeRasterLayer(QgsRasterLayer):

    def __init__(self, terraqube_cloud, url, name, canvas, hiperqube_id):
        self._terraqube_cloud = terraqube_cloud
        filename = self._terraqube_cloud.download_file(url)
        QgsRasterLayer.__init__(self, filename, name)
        self._hiperqube_id = hiperqube_id
        self._signatures = []
        self._canvas = canvas

    def hiperqube_id(self):
        return self._hiperqube_id
    
    def find_signature(self, signature_id):
        for s in self._signatures:
            if signature_id == s['id']:
                return s

    def add_signature(self, signature):
        s = self.find_signature(signature['id'])
        if s:
            remove_signature(s)
        signature[MARKERS_KEY] = []
        self._signatures.append(signature)
        m = QgsVertexMarker(self._canvas)
        col = signature['col']
        line = signature['line']
        point = QgsPointXY(col, -line)
        m.setCenter(point)
        filename = self._terraqube_cloud.download_file(signature['url'])
        i = SignatureCanvasItem(self._canvas, filename, point)
        signature[MARKERS_KEY].append(m)
        signature[MARKERS_KEY].append(i)

    def remove_signature(self, signature):
        self._signatures.remove(signature)
        self.remove_markers(signature)

    def set_signature_visibility(self, signature, visibility):
        s = self.find_signature(signature['id'])
        if s:
            for m in s[MARKERS_KEY]:
                if visibility:
                    m.show()
                else:
                    m.hide()
        else:
            self.add_signature(signature)
    
    def remove_markers(self, signature):
        for m in signature[MARKERS_KEY]:
            self._canvas.scene().removeItem(m)

    def unload(self):
        for s in self._signatures:
            self.remove_markers(s)
