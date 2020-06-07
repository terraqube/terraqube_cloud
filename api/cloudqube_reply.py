class CloudqubeReply:
    def __init__(self, reply, error):
        self._reply = reply
        self._error = error
        reply.error.connect(self.error)

    def error(self, error):
        self._error(error, self._reply.errorString())

    def abort(self):
        self._reply.abort()
