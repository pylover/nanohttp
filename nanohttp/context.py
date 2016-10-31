
import threading
import wsgiref.util
import wsgiref.headers

from nanohttp.proxy import ObjectProxy
from nanohttp.helpers import lazy_attribute


thread_local = threading.local()


class Context(dict):

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.headers = wsgiref.headers.Headers()

    def __enter__(self):
        thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del thread_local.nanohttp_context

    @classmethod
    def get_current(cls):
        return thread_local.nanohttp_context

    @lazy_attribute
    def method(self):
        return self.environ['REQUEST_METHOD'].lower()

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @lazy_attribute
    def uri(self):
        return wsgiref.util.request_uri(self.environ, include_query=True)

    @lazy_attribute
    def scheme(self):
        return wsgiref.util.guess_scheme(self.environ)

    @lazy_attribute
    def request_encoding(self):
        raise NotImplementedError

    @lazy_attribute
    def response_encoding(self):
        raise NotImplementedError


context = ObjectProxy(Context.get_current)
