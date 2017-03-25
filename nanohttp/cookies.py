
import time
from datetime import datetime

from .configuration import settings
from .constants import HTTP_DATETIME_FORMAT


class HttpCookie(object):
    """
    HTTP Cookie
    http://www.ietf.org/rfc/rfc2109.txt

    ``domain``, ``secure`` and ``http_only`` are taken from ``config`` if not set.
    """
    __slots__ = ('name', 'value', 'path', 'expires',
                 'domain', 'secure', 'http_only')

    def __init__(self, name, value=None, path='/', expires=None, max_age=None, domain=None, secure=None,
                 http_only=None):
        self.name = name
        self.value = value
        self.path = path
        if max_age is None:
            self.expires = expires
        else:
            self.expires = datetime.utcfromtimestamp(time.time() + max_age)
        if domain is None:
            self.domain = settings.domain
        else:
            self.domain = domain
        if secure is None:
            self.secure = settings.cookie.secure
        else:
            self.secure = secure
        if http_only is None:
            self.http_only = settings.cookie.http_only
        else:
            self.http_only = http_only

    @classmethod
    def delete(cls, name, **kwargs):
        """ Returns a cookie to be deleted by browser.
        """
        return cls(name, expires='Sat, 01 Jan 2000 00:00:01 GMT', **kwargs)

    def http_set_cookie(self):
        """ Returns Set-Cookie response header.
        """
        directives = []
        append = directives.append
        append(self.name + '=')
        if self.value:
            append(self.value)
        if self.domain:
            append('; domain=%s' % self.domain)
        if self.expires:
            append('; expires=%s' % (
                self.expires if isinstance(self.expires, str)
                else self.expires.strftime(HTTP_DATETIME_FORMAT))
            )
        if self.path:
            append('; path=%s' % self.path)
        if self.secure:
            append('; secure')
        if self.http_only:
            append('; httponly')
        return 'Set-Cookie', ''.join(directives)
