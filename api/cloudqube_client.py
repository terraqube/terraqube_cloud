import gzip
import json
import os.path
import pytz.reference
import requests
import tempfile
import time

from qgis.PyQt.QtCore import QUrl, QByteArray, QFile, QIODevice
from qgis.PyQt.QtNetwork import QNetworkRequest
from qgis.core import QgsMessageLog, Qgis, QgsNetworkAccessManager
from .requests_toolbelt import MultipartEncoder
from .cloudqube_json_reply import CloudqubeJsonReply
from .cloudqube_file_reply import CloudqubeFileReply
from .login_callback import LoginCallback

UPLOAD_CHUNK_SIZE = 128 * 1024


class CloudqubeClient:
    """Handles calls to Terraqube Cloud."""

    def __init__(self, server):
        self._nam = QgsNetworkAccessManager()
        self._server = server
        self._token = None
        self._replies = []

    # Private methods
    def get_url(self, url):
        return "{0}/terraqube/cloudqube/1.0.0/{1}".format(self._server, url)

    def post(self, url, data={}, content_type="application/json"):
        url = self.get_url(url)
        headers = {
            "Accept": "application/json",
            "Content-type": content_type
        }
        if self._token:
            headers["Authorization"] = "Bearer {0}".format(self._token)
        if content_type == 'application/json':
            data = json.dumps(data)
        return requests.post(
            url,
            data=data,
            headers=headers)

    def get(self, url, content_type="application/json"):
        url = self.get_url(url)
        headers = {
            "Accept": "application/json",
            "Content-type": content_type
        }
        if self._token:
            headers["Authorization"] = "Bearer {0}".format(self._token)
        return requests.get(
            url,
            headers=headers)

    def finished(self, reply):
        self._replies.remove(reply)

    def set_token(self, token):
        self._token = token

    def str_to_byte_array(self, input_string):
        return bytes(input_string, encoding='utf-8')

    def byte_array_to_string(self, byte_array):
        return byte_array.data().decode('utf-8')

    def prepare_request(self, url, content_type):
        url = self.get_url(url)
        req = QNetworkRequest(QUrl(url))
        req.setHeader(QNetworkRequest.ContentTypeHeader, content_type)
        req.setRawHeader(b'Accept', b'application/json')
        if self._token:
            req.setRawHeader(b'Authorization', self.str_to_byte_array(
                'Bearer {0}'.format(self._token)))
        return req

    def get_nam(self, url, callback, error, content_type='application/json'):
        req = self.prepare_request(url, content_type)
        self._replies.append(CloudqubeJsonReply(
            self._nam.get(req), None, callback, self.finished, error))

    def post_json_nam(self, url, data, callback, error, content_type='application/json'):
        req = self.prepare_request(url, content_type)
        byte_array = self.str_to_byte_array(json.dumps(data)) if data else None
        self._replies.append(CloudqubeJsonReply(self._nam.post(
            req, byte_array), data, callback, self.finished, error))

    def post_bytes_nam(self, url, data, callback, error, content_type='application/octet-stream'):
        req = self.prepare_request(url, content_type)
        self._replies.append(CloudqubeJsonReply(self._nam.post(
            req, data), data, callback, self.finished, error))

    # Public methods

    def login_user(self, username, password, callback, error):
        """Login user to Terraqube Cloud using username and password."""
        login_callback = LoginCallback(self, callback)
        response = self.post_json_nam(
            "user/login", {"username": username, "password": password}, login_callback.notify, error)

    def get_projects(self, callback, error):
        """Get list of projects for current user."""
        self.get_nam("projects", callback, error)

    def get_hiperqubes(self, project_id, callback, error):
        """Get list of hiperqubes for current user."""
        self.get_nam(
            "projects/{0}/hiperqubes".format(project_id), callback, error)

    def get_hiperqube_details(self, hiperqube_id, callback, error):
        """Get hiperqube details."""
        self.get_nam("hiperqubes/{0}".format(hiperqube_id), callback, error)

    def create_hiperqube(self, project_id, name, captured_date, callback, error):
        """Create a new hiperqube."""
        captured_date = captured_date.replace(microsecond=0).replace(
            tzinfo=pytz.reference.LocalTimezone())
        captured_date_str = captured_date.isoformat()
        payload = {
            'name': name,
            'capturedDate': captured_date_str
        }
        self.post_json_nam(
            "projects/{0}/hiperqubes".format(project_id), payload, callback, error)

    def upload_hiperqube_hdr(self, hiperqube_id, filename, callback, error):
        """Upload an HDR file to an existing hiperqube."""
        f = QFile(filename)
        f.open(QIODevice.ReadOnly)
        self.post_bytes_nam('hiperqubes/{0}/hdr'.format(hiperqube_id), f, callback, error, content_type='application/octet-stream')

    def upload_hiperqube_bil(self, url, fields, filename, callback):
        """Upload an BIL file to an existing hiperqube."""
        with open(filename, 'rb') as f:
            fields['file'] = (filename, ProgressFileWrapper(
                f, callback))
            m = MultipartEncoder(fields=fields)
            response = requests.post(url, data=m, headers={
                                     'Content-Type': m.content_type})
        if not response.ok:
            response.raise_for_status()

    def create_signature(self, hiperqube_id, row, col, callback, error):
        """Creates a new signature of the given row and col."""
        self.post_json_nam(
            "hiperqubes/{0}/signatures?line={1}&col={2}".format(hiperqube_id, row, col), None, callback, error)

    def get_signatures(self, hiperqube_id, callback, error):
        """Gets all signatures from a hiperqube."""
        self.get_nam(
            "hiperqubes/{0}/signatures".format(hiperqube_id), callback, error)

    def download_file(self, uri, callback, error):
        """Downloads the file in the uri in a temporary file and returns its name."""
        req = QNetworkRequest(QUrl(uri))
        reply = CloudqubeFileReply(self._nam.get(req), callback, self.finished, error)
        self._replies.append(reply)
        return reply.filename()


class ProgressFileWrapper(object):
    def __init__(self, file, callback):
        self._file = file
        self.callback = callback

    def read(self, amt=None):
        time.sleep(1)
        if not amt:
            amt = UPLOAD_CHUNK_SIZE
        buf = self._file.read(UPLOAD_CHUNK_SIZE)
        QgsMessageLog.logMessage(
            "Read {0} bytes of data.".format(len(buf)), level=Qgis.Info)
        self.callback(len(buf))
        return buf

    def __getattr__(self, name):
        return getattr(self._file, name)
