
import io
import unittest

from nanohttp import Controller, action


class DispatcherTestCase(unittest.TestCase):

    def test_dispatcher(self):

        response = io.BytesIO()
        environ = {}

        def start_response(status, headers):
            response.write(b'%s\n' % status.encode())
            for k, v in headers:
                response.write(b'%s:%s\n' % (k.encode(), v.encode()))

        class Root(Controller):

            @action()
            def index(self):
                return 'Index'

            @action(method='post')
            def index(self):
                return 'Index'

        app = Root()
        app(environ, start_response)




