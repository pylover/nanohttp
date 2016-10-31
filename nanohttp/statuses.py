class HttpStatus(Exception):
    status_code = None
    status_text = None

    def __init__(self, message=None):
        super().__init__(message or self.status_text)

    @property
    def status(self):
        return '%s %s' % (self.status_code, self.status_text)

    def render(self):
        yield self.status.encode()


class HttpBadRequest(HttpStatus):
    status_code = 400
    status_text = 'Bad request'


class HttpUnauthorized(HttpStatus):
    status_code = 401
    status_text = 'You need to be authenticated'


class HttpForbidden(HttpStatus):
    status_code = 403
    status_text = 'Access denied'


class HttpNotFound(HttpStatus):
    status_code = 404
    status_text = 'Not Found'


class HttpConflict(HttpStatus):
    status_code = 409
    status_text = 'Conflict'


class HttpGone(HttpStatus):
    status_code = 410
    status_text = 'Access to resource is no longer available. Please contact us to find the reason.'


class HttpMethodNotAllowed(HttpStatus):
    status_code = 405
    status_text = 'Method not allowed'


class InternalServerError(HttpStatus):
    status_code = 500
    status_text = 'Internal server error'
