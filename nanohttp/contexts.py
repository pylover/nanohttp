
import threading
import wsgiref.util
import wsgiref.headers

from typing import Union
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

from nanohttp import exceptions
from .helpers import LazyAttribute, parse_any_form


class ContextIsNotInitializedError(Exception):
    pass


class ContextStack(list):

    def push(self, item):
        self.append(item)


class Context:
    """A Global context for Request and Response.

    Context are initialized and entering on every request (referring to
     nanohttp application lifecycle).

    Context also supports to use stack nested (>=0.16.6), its useful on
    testing.

    .. code-block:: python

        def sample:
            return context.query['weather']

        with Context({'QUERY_STRING': 'weather=Sunny'}):
            assert sample() == 'Sunny

            with Context({'QUERY_STRING': 'weather=Rainy'}):
                assert sample() == 'Rainy'

    """

    #: Response encoding
    response_encoding = None

    #: Thread local variable contexts stored in
    thread_local = threading.local()

    #: Current :class:`.Application` instance
    application = None

    @property
    def __stack__(self):
        """Nested contexts stack
        """
        THREADLOCAL_STACK_ATTRIBUTE = 'nanohttp_context_stack'
        if not hasattr(self.thread_local, THREADLOCAL_STACK_ATTRIBUTE):
            setattr(
                self.thread_local, THREADLOCAL_STACK_ATTRIBUTE, ContextStack()
            )
        return getattr(self.thread_local, THREADLOCAL_STACK_ATTRIBUTE)

    def __init__(self, environ, application=None):
        """
        :param environ: WSGI environ dictionary
        :param application: :class:`.Application` instance
        """
        self.environ = environ
        self.application = application
        self.response_headers = wsgiref.headers.Headers()

    def __enter__(self):
        # Backing up the current context
        if hasattr(self.thread_local, 'nanohttp_context'):
            self.__stack__.push(self.thread_local.nanohttp_context)

        self.thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.thread_local.nanohttp_context
        if self.__stack__:
            self.thread_local.nanohttp_context = self.__stack__.pop()

    @LazyAttribute
    def request_content_length(self) -> Union[int, None]:
        """Request content length
        """
        v = self.environ.get('CONTENT_LENGTH')
        return None if not v or not v.strip() else int(v)

    @LazyAttribute
    def request_content_type(self) -> Union[str, None]:
        """Request content type
        """
        content_type = self.environ.get('CONTENT_TYPE')
        if content_type:
            return content_type.split(';')[0]
        return None

    @property
    def response_content_type(self) -> Union[str, None]:
        """Response content type property
        """
        content_type = self.response_headers.get('Content-Type')
        if content_type:
            return content_type.split(';')[0]
        return None

    @response_content_type.setter
    def response_content_type(self, v):
        if v is None:
            del self.response_headers['Content-Type']
        else:
            self.response_headers['Content-Type'] = \
                '%s; charset=%s' % (v, self.response_encoding)

    @classmethod
    def get_current(cls) -> 'Context':
        """Get current context

            Not initialized context raises
            :class:`.ContextIsNotInitializedError`,
        """
        if not hasattr(cls.thread_local, 'nanohttp_context'):
            raise ContextIsNotInitializedError(
                "Context is not initialized yet."
            )
        return cls.thread_local.nanohttp_context

    @LazyAttribute
    def method(self):
        """`HTTP Request method
        <https://tools.ietf.org/html/rfc7231#section-4.3>`_
        """
        return self.environ['REQUEST_METHOD'].lower()

    @LazyAttribute
    def path(self):
        """Request path
        """
        return self.environ['PATH_INFO']

    @LazyAttribute
    def request_uri(self):
        """Request full URI (includes query string)
        """
        return wsgiref.util.request_uri(self.environ, include_query=True)

    @LazyAttribute
    def request_scheme(self):
        """Request Scheme (http|https)
        """
        return wsgiref.util.guess_scheme(self.environ)

    @LazyAttribute
    def query(self):
        """Request query string
        """
        if 'QUERY_STRING' not in self.environ:
            return {}

        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}

    @LazyAttribute
    def form(self):
        """Request form values

        .. note:: if using `multipart/form-data` uploaded file will reproduce
         as ``cgi.FieldStorage``.
        """
        return parse_any_form(
            self.environ,
            content_length=self.request_content_length,
            content_type=self.request_content_type
        )

    @LazyAttribute
    def cookies(self) -> 'SimpleCookie':
        """Cookies
        """
        result = SimpleCookie()
        if 'HTTP_COOKIE' in self.environ:
            result.load(self.environ['HTTP_COOKIE'])
        return result

    def encode_response(self, buff):
        """Encode response buffer with encoding definition on current
        context
        """
        try:
            if self.response_encoding:
                return buff.encode(self.response_encoding)
            else:
                return buff
        except AttributeError:
            raise TypeError(
                'The returned response should has the `encode` attribute, '
                'such as `str`.'
            )


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
