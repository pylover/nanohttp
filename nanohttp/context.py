
import threading

from nanohttp.proxy import ObjectProxy
from nanohttp.helpers import lazy_attribute


thread_local = threading.local()


class Context(dict):

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.headers = []

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


context = ObjectProxy(Context.get_current)
