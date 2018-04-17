
import abc
import ujson
import traceback

from .contexts import context
from .configuration import settings


class HttpStatus(Exception, metaclass=abc.ABCMeta):
    status_code = None
    status_text = None
    info = None

    @abc.abstractmethod
    def __init__(self, message):
        super().__init__(message)

    @property
    def status(self):
        return '%s %s' % (self.status_code, self)

    def to_dict(self):
        return dict(
            message=self.status_text,
            description=self.info
        )

    def render(self):
        if context.response_content_type == 'application/json':
            return ujson.encode(self.to_dict())
        else:
            context.response_encoding = 'utf-8'
            context.response_content_type = 'text/plain'
            return "%s\n%s" % (self.status_text, self.info)


class PreDefinedHttpStatus(HttpStatus):

    def __init__(self, message=None, reason=None, info=None):
        if info is not None:
            self.info = info

        if reason:
            context.response_headers.add_header('X-Reason', reason)
        super().__init__(message or self.status_text)


class HttpCustomStatus(HttpStatus):

    def __init__(self, status_text=None, reason=None, info=None, status_code=None):
        if info is not None:
            self.info = info

        if status_code is not None:
            self.status_code = status_code

        if status_text is not None:
            self.status_text = status_text

        if reason:
            context.response_headers.add_header('X-Reason', reason)
        super().__init__(self.status_text)


class HttpBadRequest(PreDefinedHttpStatus):
    status_code, status_text, info = 400, 'Bad Request', 'Bad request syntax or unsupported method'


class HttpUnauthorized(PreDefinedHttpStatus):
    status_code, status_text, info = 401, 'Unauthorized', 'No permission -- see authorization schemes'


class HttpForbidden(PreDefinedHttpStatus):
    status_code, status_text, info = 403, 'Forbidden', 'Request forbidden -- authorization will not help'


class HttpNotFound(PreDefinedHttpStatus):
    status_code, status_text, info = 404, 'Not Found', 'Nothing matches the given URI'


class HttpMethodNotAllowed(PreDefinedHttpStatus):
    status_code, status_text, info = 405, 'Method Not Allowed', 'Specified method is invalid for this resource'


class HttpConflict(PreDefinedHttpStatus):
    status_code, status_text, info = 409, 'Conflict', 'Request conflict'


class HttpGone(PreDefinedHttpStatus):
    status_code, status_text, info = 410, 'Gone', 'URI no longer exists and has been permanently removed'


class HttpPreconditionFailed(PreDefinedHttpStatus):
    status_code, status_text, info = 412, 'Precondition Failed', 'Request cannot be fulfilled'


class HttpRedirect(PreDefinedHttpStatus):
    """
    This is an abstract class for all redirects.
    """

    def __init__(self, location, *args, **kw):
        context.response_headers.add_header('Location', location)
        super().__init__(*args, **kw)


class HttpMovedPermanently(HttpRedirect):
    status_code, status_text, info = 301, 'Moved Permanently', 'Object moved permanently'


class HttpFound(HttpRedirect):
    status_code, status_text, info = 302, 'Found', 'Object moved temporarily'


class HttpNotModified(PreDefinedHttpStatus):
    status_code, status_text, info = 304, 'Not Modified', ''  # 304 is only header


class HttpInternalServerError(PreDefinedHttpStatus):
    status_code, status_text = 500, 'Internal Server Error'

    @property
    def info(self):
        if settings.debug:
            return traceback.format_exc()
        return 'Server got itself in trouble'


class HttpBadGatewayError(PreDefinedHttpStatus):
    status_code, status_text = 502, 'Bad Gateway'
