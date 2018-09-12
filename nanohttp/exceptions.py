import ujson
import traceback

from .contexts import context
from .configuration import settings


class HTTPStatus(Exception):
    status = None
    headers = None

    def __init__(self, status=None):
        if status is not None:
            self.status = status

        super().__init__(self.status)

    def render(self):
        stack_trace = traceback.format_exc()
        if context.response_content_type == 'application/json':
            return ujson.encode(
                dict(stackTrace=stack_trace) if settings.debug else dict()
            )
        context.response_encoding = 'utf-8'
        context.response_content_type = 'text/plain'
        return stack_trace if settings.debug \
            else self.status.split(' ', 1)[1]

    @property
    def headers(self):
        if context.response_content_type == 'application/json':
            contenttype = context.response_content_type
        else:
            contenttype = 'text/plain;charset=utf-8'

        return [('ContentType', contenttype)]


class HTTPKnownStatus(HTTPStatus):
    def __init__(self, status_text=None):
        code, text = self.status.split(' ', 1)
        super().__init__(f'{code} {status_text or text}')


class HTTPBadRequest(HTTPKnownStatus):
    status = '400 Bad Request'


class HTTPUnauthorized(HTTPKnownStatus):
    status = '401 Unauthorized'


class HTTPForbidden(HTTPKnownStatus):
    status = '403 Forbidden'


class HTTPNotFound(HTTPKnownStatus):
    status = '404 Not Found'


class HTTPMethodNotAllowed(HTTPKnownStatus):
    status = '405 Method Not Allowed'


class HTTPConflict(HTTPKnownStatus):
    status = '409 Conflict'


class HTTPGone(HTTPKnownStatus):
    status = '410 Gone'


class HTTPPreconditionFailed(HTTPKnownStatus):
    status = '412 Precondition Failed'


class HTTPRedirect(HTTPKnownStatus):
    """
    This is an abstract class for all redirects.
    """

    def __init__(self, location, *args, **kw):
        self._headers = [('Location', location)]
        super().__init__(*args, **kw)

    @property
    def headers(self):
        headers = super().headers
        return headers + self._headers


class HTTPMovedPermanently(HTTPRedirect):
    status = '301 Moved Permanently'


class HTTPFound(HTTPRedirect):
    status = '302 Found'


class HTTPNotModified(HTTPKnownStatus):
    status = '304 Not Modified'


class HTTPInternalServerError(HTTPKnownStatus):
    status = '500 Internal Server Error'


class HTTPBadGatewayError(HTTPKnownStatus):
    status = '502 Bad Gateway'


class HTTPSuccess(HTTPKnownStatus):
    status = '200 OK'


class HTTPCreated(HTTPSuccess):
    status = '201 Created'


class HTTPAccepted(HTTPSuccess):
    status = '202 Accepted'


class HTTPNonAuthoritativeInformation(HTTPSuccess):
    status = '203 Non-Authoritative Information'


class HTTPNoContent(HTTPSuccess):
    status = '204 No Content'


class HTTPResetContent(HTTPSuccess):
    status = '205 Reset Content'


class HTTPPartialContent(HTTPSuccess):
    status = '206 Partial Content'
