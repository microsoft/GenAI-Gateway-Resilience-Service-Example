class ApiException(Exception):
    """
    ApiException for general exceptions in REST api app.
    """

    def __init__(self, message, error_code=None, status_code=500):
        super(ApiException, self).__init__(message)
        self._error_code = error_code
        self._status_code = status_code
        self._message = message

    @property
    def error_code(self):
        return self._error_code

    @property
    def status_code(self):
        return self._status_code

    @property
    def message(self):
        return self._message
