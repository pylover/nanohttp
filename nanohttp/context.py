
import threading
import wsgiref.util
import wsgiref.headers
from urllib.parse import parse_qs

from nanohttp.proxy import ObjectProxy
from nanohttp.helpers import lazy_attribute


thread_local = threading.local()


class Context(dict):
    response_encoding = 'utf8'

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.headers = wsgiref.headers.Headers()

    def __enter__(self):
        thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del thread_local.nanohttp_context

    @property
    def response_content_type(self):
        return self.headers.get('Content-Type')

    @response_content_type.setter
    def response_content_type(self, v):
        self.headers['Content-Type'] = v

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
    def query_string(self):
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}


context = ObjectProxy(Context.get_current)
