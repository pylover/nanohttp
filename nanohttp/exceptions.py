
import ujson
import traceback

from .contexts import context
from .configuration import settings


class HttpStatus(Exception):
    status = None

    def __init__(self, status=None):
        if status is not None:
            self.status = status

        super().__init__(self.status)

    def to_dict(self):
        return dict()

    def render(self):
        if context.response_content_type == 'application/json':
            return ujson.encode(self.to_dict())
        else:
            context.response_encoding = 'utf-8'
            context.response_content_type = 'text/plain'
            return self.status


class HttpBadRequest(HttpStatus):
    status = '400 Bad Request'


class HttpUnauthorized(HttpStatus):
    status = '401 Unauthorized'


class HttpForbidden(HttpStatus):
    status = '403 Forbidden'


class HttpNotFound(HttpStatus):
    status = '404 Not Found'


class HttpMethodNotAllowed(HttpStatus):
    status = '405 Method Not Allowed'


class HttpConflict(HttpStatus):
    status = '409 Conflict'


class HttpGone(HttpStatus):
    status = '410 Gone'


class HttpPreconditionFailed(HttpStatus):
    status = '412 Precondition Failed'


class HttpRedirect(HttpStatus):
    """
    This is an abstract class for all redirects.
    """

    def __init__(self, location, *args, **kw):
        context.response_headers.add_header('Location', location)
        super().__init__(*args, **kw)


class HttpMovedPermanently(HttpRedirect):
    status = '301 Moved Permanently'


class HttpFound(HttpRedirect):
    status = '302 Found'


class HttpNotModified(HttpStatus):
    status = '304 Not Modified'


class HttpInternalServerError(HttpStatus):
    status = '500 Internal Server Error'

    @property
    def info(self):
        if settings.debug:
            return traceback.format_exc()
        return 'Server got itself in trouble'


class HttpBadGatewayError(HttpStatus):
    status = '502 Bad Gateway'
