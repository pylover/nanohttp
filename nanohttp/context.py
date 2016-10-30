
import threading

from nanohttp.proxy import ObjectProxy
from nanohttp.helpers import lazy_attribute


class Context(dict):

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.headers = []

    def __enter__(self):
        setattr(threading.local(), '_nanohttp_context', self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        delattr(threading.local(), '_nanohttp_context')

    @classmethod
    def get_current(cls):
        return getattr(threading.local(), '_nanohttp_context')

    @lazy_attribute
    def method(self):
        return self.environ['REQUEST_METHOD'].lower()

    @property
    def path(self):
        return self.environ['PATH_INFO']


context = ObjectProxy(Context.get_current)
