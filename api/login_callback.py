class LoginCallback:
    def __init__(self, cloudqube, callback):
        self._cloudqube = cloudqube
        self._callback = callback

    def notify(self, data):
        self._cloudqube.set_token(data['access_token'])
        self._callback(data)
