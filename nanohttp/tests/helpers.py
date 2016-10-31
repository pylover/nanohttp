
import httplib2
from wsgi_intercept.interceptor import Httplib2Interceptor


class WsgiTester(httplib2.Http):

    def __init__(self, app_factory, host='nanohttp.org', port=80, **kw):
        super(WsgiTester, self).__init__()
        self.interceptor = Httplib2Interceptor(app_factory, host=host, port=port, **kw)

    def __enter__(self):
        self.interceptor.__enter__()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.interceptor.__exit__(exc_type, value, traceback)

    def _do_request(self, uri, method, **kw):
        return self.request('%s%s' % (self.interceptor.url, uri), method=method.upper(), **kw)

    def get(self, uri, **kw):
        return self._do_request(uri, 'get', **kw)

    def post(self, uri, **kw):
        return self._do_request(uri, 'post', **kw)