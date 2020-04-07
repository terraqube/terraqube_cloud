import gzip
import json
import os.path
import pytz.reference
import requests
import tempfile
import time

from qgis.core import QgsMessageLog, Qgis
from .requests_toolbelt import MultipartEncoder

UPLOAD_CHUNK_SIZE = 128 * 1024


class CloudqubeClient:
    def __init__(self, server):
        self.server = server
        self.token = None

    def get_url(self, url):
        return "{0}/terraqube/cloudqube/1.0.0/{1}".format(self.server, url)

    def post(self, url, data={}, content_type="application/json"):
        url = self.get_url(url)
        headers = {
            "accepts": "application/json",
            "Content-type": content_type
        }
        if self.token:
            headers["Authorization"] = "Bearer {0}".format(self.token)
        if content_type == 'application/json':
            data = json.dumps(data)
        return requests.post(
            url,
            data=data,
            headers=headers)

    def get(self, url, data={}, content_type="application/json"):
        url = self.get_url(url)
        headers = {
            "accepts": "application/json",
            "Content-type": content_type
        }
        if self.token:
            headers["Authorization"] = "Bearer {0}".format(self.token)
        return requests.get(
            url,
            params=data,
            headers=headers)

    def login_user(self, username, password):
        """Login user to Terraqube Cloud using username and password."""
        response = self.post(
            "user/login", {"username": username, "password": password})
        if response.ok:
            data = response.json()
            self.token = data['access_token']
        else:
            response.raise_for_status()

    def get_projects(self):
        """Get list of projects for current user."""
        response = self.get("projects")
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_hiperqubes(self, project_id):
        """Get list of hiperqubes for current user."""
        response = self.get("projects/{0}/hiperqubes".format(project_id))
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def get_hiperqube_details(self, hiperqube_id):
        """Get hiperqube details."""
        response = self.get("hiperqubes/{0}".format(hiperqube_id))
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def create_hiperqube(self, project_id, name, captured_date):
        """Create a new hiperqube."""
        captured_date = captured_date.replace(microsecond=0).replace(
            tzinfo=pytz.reference.LocalTimezone())
        captured_date_str = captured_date.isoformat()
        payload = {
            'name': name,
            'capturedDate': captured_date_str
        }
        response = self.post(
            "projects/{0}/hiperqubes".format(project_id), data=payload)
        if response.ok:
            return response.json()
        else:
            response.raise_for_status()

    def upload_hiperqube_hdr(self, hiperqube_id, filename):
        """Upload an HDR file to an existing hiperqube."""
        with open(filename, 'rb') as f:
            response = self.post(
                'hiperqubes/{0}/hdr'.format(hiperqube_id), data=f, content_type='application/octet-stream')
            if not response.ok:
                response.raise_for_status()

    def upload_hiperqube_bil(self, url, fields, filename, callback):
        """Upload an BIL file to an existing hiperqube."""
#        if filename.endswith('.gz'):
        with open(filename, 'rb') as f:
            fields['file'] = (filename,ProgressFileWrapper(
                f, callback))
            m = MultipartEncoder(fields=fields)
            response = requests.post(url, data=m, headers={'Content-Type': m.content_type})
#        else:
#            buf = io.BytesIO()
#            with open(filename, 'rb') as src:
#                with gzip.GzipFile(fileobj=buf, mode='wb') as dst:
#                    response = self.post(url, data=self.upload_gen(src, dst, callback), content_type='application/octet-stream')
        if not response.ok:
            response.raise_for_status()

    def download_file(self, uri):
        """Downloads the file in the uri in a temporary file and returns its name."""
        filename = None
        response = requests.get(uri)
        if response.ok:
            try:
                extension = '.{0}'.format(response.headers['content-type'].split('/')[1])
            except:
                extension = ''
            _, filename = tempfile.mkstemp()
            with open(filename, 'wb') as f:
                f.write(response.content)
        else:
            response.raise_for_status()
        return filename
            
            


class ProgressFileWrapper(object):
    def __init__(self, file, callback):
        self._file = file
        self.callback = callback

    def read(self, amt=None):
        time.sleep(1)
        if not amt:
            amt = UPLOAD_CHUNK_SIZE
        buf = self._file.read(UPLOAD_CHUNK_SIZE)
        QgsMessageLog.logMessage("Read {0} bytes of data.".format(len(buf)), level=Qgis.Info)
        self.callback(len(buf))
        return buf


    def __getattr__(self, name):
        return getattr(self._file, name)