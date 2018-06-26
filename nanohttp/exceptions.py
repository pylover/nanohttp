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

    def render(self):
        stack_trace = traceback.format_exc()
        if context.response_content_type == 'application/json':
            return ujson.encode(
                dict(
                    stackTrace=stack_trace) if settings.debug else dict()
            )
        else:
            context.response_encoding = 'utf-8'
            context.response_content_type = 'text/plain'
            return stack_trace if settings.debug else ''


class HttpKnownStatus(HttpStatus):
    def __init__(self, status_text=None):
        code, text = self.status.split(' ', 1)
        super().__init__(f'{code} {status_text or text}')


class HttpBadRequest(HttpKnownStatus):
    status = '400 Bad Request'


class HttpUnauthorized(HttpKnownStatus):
    status = '401 Unauthorized'


class HttpForbidden(HttpKnownStatus):
    status = '403 Forbidden'


class HttpNotFound(HttpKnownStatus):
    status = '404 Not Found'


class HttpMethodNotAllowed(HttpKnownStatus):
    status = '405 Method Not Allowed'


class HttpConflict(HttpKnownStatus):
    status = '409 Conflict'


class HttpGone(HttpKnownStatus):
    status = '410 Gone'


class HttpPreconditionFailed(HttpKnownStatus):
    status = '412 Precondition Failed'


class HttpRedirect(HttpKnownStatus):
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


class HttpNotModified(HttpKnownStatus):
    status = '304 Not Modified'


class HttpInternalServerError(HttpKnownStatus):
    status = '500 Internal Server Error'


class HttpBadGatewayError(HttpKnownStatus):
    status = '502 Bad Gateway'


class HttpSuccess(HttpKnownStatus):
    status = '200 OK'


class HttpCreated(HttpSuccess):
    status = '201 Created'


class HttpAccepted(HttpSuccess):
    status = '202 Accepted'


class HttpNonAuthoritativeInformation(HttpSuccess):
    status = '203 Non-Authoritative Information'


class HttpNoContent(HttpSuccess):
    status = '204 No Content'


class HttpResetContent(HttpSuccess):
    status = '205 Reset Content'


class HttpPartialContent(HttpSuccess):
    status = '206 Partial Content'
