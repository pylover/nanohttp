
import threading
import cgi
import wsgiref.util
import wsgiref.headers
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

import ujson

from nanohttp import exceptions
from .helpers import LazyAttribute


class ContextIsNotInitializedError(Exception):
    pass


# FIXME: use __slots__
class Context(object):
    response_encoding = None
    thread_local = threading.local()
    application = None

    def __init__(self, environ, application=None):
        super(Context, self).__init__()
        self.environ = environ
        self.application = application
        self.response_headers = wsgiref.headers.Headers()

    def __enter__(self):
        self.thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.thread_local.nanohttp_context

    @LazyAttribute
    def request_content_length(self):
        v = self.environ.get('CONTENT_LENGTH')
        return None if v is None else int(v)

    @LazyAttribute
    def request_content_type(self):
        content_type = self.environ.get('CONTENT_TYPE')
        if content_type:
            return content_type.split(';')[0]
        return None

    @property
    def response_content_type(self):
        content_type = self.response_headers.get('Content-Type')
        if content_type:
            return content_type.split(';')[0]
        return None

    @response_content_type.setter
    def response_content_type(self, v):
        self.response_headers['Content-Type'] = '%s; charset=%s' % (v, self.response_encoding)

    @classmethod
    def get_current(cls):
        if not hasattr(cls.thread_local, 'nanohttp_context'):
            raise ContextIsNotInitializedError("Context is not initialized yet.")
        return cls.thread_local.nanohttp_context

    @LazyAttribute
    def method(self):
        return self.environ['REQUEST_METHOD'].lower()

    @LazyAttribute
    def path(self):
        return self.environ['PATH_INFO']

    @LazyAttribute
    def request_uri(self):
        return wsgiref.util.request_uri(self.environ, include_query=True)

    @LazyAttribute
    def request_scheme(self):
        return wsgiref.util.guess_scheme(self.environ)

    @LazyAttribute
    def query_string(self):
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}

    @LazyAttribute
    def form(self):
        result = {}

        if self.request_content_type == 'application/json':
            fp = self.environ['wsgi.input']
            data = fp.read(self.request_content_length)
            return ujson.decode(data)

        try:
            storage = cgi.FieldStorage(
                fp=self.environ['wsgi.input'],
                environ=self.environ,
                strict_parsing=False,
                keep_blank_values=True
            )
        except TypeError:
            raise exceptions.HttpBadRequest('Cannot parse the request.')

        if storage.list is None or not len(storage.list):
            return {}

        def get_value(f):
            # noinspection PyProtectedMember
            return f.value if isinstance(f,  cgi.MiniFieldStorage) \
                              or (isinstance(f, cgi.FieldStorage) and not f._binary_file) else f

        for k in storage:

            v = storage[k]

            if isinstance(v, list):
                result[k] = [get_value(i) for i in v]
            else:
                result[k] = get_value(v)

        return result

    @LazyAttribute
    def cookies(self):
        result = SimpleCookie()
        if 'HTTP_COOKIE' in self.environ:
            result.load(self.environ['HTTP_COOKIE'])
        return result

    def encode_response(self, buffer):
        try:
            if self.response_encoding:
                return buffer.encode(self.response_encoding)
            else:
                return buffer
        except AttributeError:  # pragma: no cover
            raise TypeError('The returned response should has the `encode` attribute, such as `str`.')


class ContextProxy(Context):

    # noinspection PyInitNewSignature
    def __new__(cls) -> Context:
        type_proxy = type('ContextProxy', (object, ), {
            '__getattr__': cls.__getattr__,
            '__setattr__': cls.__setattr__,
            '__delattr__': cls.__delattr__
        })
        # noinspection PyTypeChecker
        return object.__new__(type_proxy)

    def __getattr__(self, key):
        return getattr(Context.get_current(), key)

    def __setattr__(self, key, value):
        setattr(Context.get_current(), key, value)

    def __delattr__(self, key):
        delattr(Context.get_current(), key)


context = ContextProxy()
