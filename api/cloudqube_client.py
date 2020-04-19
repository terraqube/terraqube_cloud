import gzip
import json
import os.path
import pytz.reference
import tempfile
import time

from qgis.PyQt.QtCore import QUrl, QByteArray, QFile, QIODevice, QVariant
from qgis.PyQt.QtNetwork import QNetworkRequest, QHttpMultiPart, QHttpPart
from qgis.core import QgsNetworkAccessManager
from .cloudqube_json_reply import CloudqubeJsonReply
from .cloudqube_file_reply import CloudqubeFileReply
from .cloudqube_progress_reply import CloudqubeProgressReply
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

    def get(self, url, callback, error, content_type='application/json'):
        req = self.prepare_request(url, content_type)
        self._replies.append(CloudqubeJsonReply(
            self._nam.get(req), None, callback, self.finished, error))

    def post_json(self, url, data, callback, error,
            content_type='application/json'):
        req = self.prepare_request(url, content_type)
        byte_array = self.str_to_byte_array(json.dumps(data)) if data else None
        self._replies.append(CloudqubeJsonReply(self._nam.post(
            req, byte_array), data, callback, self.finished, error))

    def post_bytes(self, url, data, callback, error,
            content_type='application/octet-stream'):
        req = self.prepare_request(url, content_type)
        self._replies.append(CloudqubeJsonReply(self._nam.post(
            req, data), data, callback, self.finished, error))

    def delete_nam(self, url, callback, error, content_type='application/json'):
        req = self.prepare_request(url, content_type)
        self._replies.append(CloudqubeJsonReply(
            self._nam.deleteResource(req), None, callback, self.finished, error))

    def add_text_parts(self, multi_part, fields):
        """Adds all text fields to the multipart object."""
        for key in fields:
            text_part = QHttpPart()
            text_part.setHeader(QNetworkRequest.ContentDispositionHeader,
                QVariant('form-data; name="{0}"'.format(key)))
            text_part.setBody(self.str_to_byte_array(fields[key]))
            multi_part.append(text_part)

    def add_image_part(self, multi_part, filename):
        """Adds the image field to the multipart object."""
        image_part = QHttpPart()
        image_part.setHeader(QNetworkRequest.ContentTypeHeader,
                             QVariant('application/octet-stream'))
        image_part.setHeader(
            QNetworkRequest.ContentDispositionHeader,
            QVariant('form-data; name="file"'))
        f = QFile(filename)
        f.open(QIODevice.ReadOnly)
        image_part.setBodyDevice(f)
        f.setParent(multi_part)
        multi_part.append(image_part)

    # Public methods

    # Authentication

    def login_user(self, username, password, callback, error):
        """Login user to Terraqube Cloud using username and password."""
        login_callback = LoginCallback(self, callback)
        response = self.post_json(
            'user/login',
            {'username': username, 'password': password},
            login_callback.notify,
            error)

    # Projects

    def create_project(self, name, callback, error):
        """Creates a new project with the specified name."""
        payload = {
            'name': name
        }
        self.post_json("projects", payload, callback, error)

    def get_projects(self, callback, error):
        """Get list of projects for current user."""
        self.get('projects', callback, error)

    def delete_project(self, project_id, callback, error):
        """Deletes a project."""
        self.delete_nam("projects/{0}".format(project_id), callback, error)

    # Hiperqubes

    def get_hiperqubes(self, project_id, callback, error):
        """Get list of hiperqubes for current user."""
        self.get(
            "projects/{0}/hiperqubes".format(project_id), callback, error)

    def get_hiperqube_details(self, hiperqube_id, callback, error):
        """Get hiperqube details."""
        self.get("hiperqubes/{0}".format(hiperqube_id), callback, error)

    def create_hiperqube(self, project_id, name, captured_date, callback,
            error):
        """Create a new hiperqube."""
        captured_date = captured_date.replace(microsecond=0).replace(
            tzinfo=pytz.reference.LocalTimezone())
        captured_date_str = captured_date.isoformat()
        payload = {
            'name': name,
            'capturedDate': captured_date_str
        }
        self.post_json(
            "projects/{0}/hiperqubes".format(project_id),
            payload,
            callback,
            error)

    def delete_hiperqube(self, hiperqube_id, callback, error):
        """Deletes a hiperqube."""
        self.delete_nam("hiperqubes/{0}".format(hiperqube_id), callback, error)

    def upload_hiperqube_hdr(self, hiperqube_id, filename, callback, error):
        """Upload an HDR file to an existing hiperqube."""
        f = QFile(filename)
        f.open(QIODevice.ReadOnly)
        self.post_bytes("hiperqubes/{0}/hdr".format(hiperqube_id),
                            f,
                            callback,
                            error,
                            content_type='application/octet-stream')

    def upload_hiperqube_bil(self, url, fields, filename, progress, callback,
            error):
        """Upload an BIL file to an existing hiperqube."""
        req = QNetworkRequest(QUrl(url))
        multi_part = QHttpMultiPart(QHttpMultiPart.FormDataType)

        self.add_text_parts(multi_part, fields)
        f = self.add_image_part(multi_part, filename)
        req = self._nam.post(req, multi_part)
        multi_part.setParent(req)
        self._replies.append(CloudqubeProgressReply(
            req, progress, callback, self.finished, error))

    # Signatures

    def create_signature(self, hiperqube_id, row, col, callback, error):
        """Creates a new signature of the given row and col."""
        payload = {
            'line': row,
            'col': col
        }
        self.post_json(
            "hiperqubes/{0}/signatures".format(hiperqube_id),
            payload,
            callback,
            error)

    def get_signatures(self, hiperqube_id, callback, error):
        """Gets all signatures from a hiperqube."""
        self.get(
            "hiperqubes/{0}/signatures".format(hiperqube_id), callback, error)

    def delete_signature(self, hiperqube_id, row, col, callback, error):
        """Deletes a signature."""
        self.delete_nam(
            "hiperqubes/{0}/signatures?line={1}&col={2}".format(
                hiperqube_id, row, col),
            callback,
            error)

    # File download

    def download_file(self, uri, callback, error):
        """Downloads the file in the uri in a temporary file and returns its
        name."""
        req = QNetworkRequest(QUrl(uri))
        reply = CloudqubeFileReply(self._nam.get(
            req), callback, self.finished, error)
        self._replies.append(reply)
        return reply.filename()
