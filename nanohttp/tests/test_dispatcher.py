
import io
import unittest

from nanohttp import Controller, action


class DispatcherTestCase(unittest.TestCase):

    @staticmethod
    def serve_app(app, url, method='get', environ=None):
        response = io.BytesIO()
        env = {
            'PATH_INFO': url,
            'REQUEST_METHOD': method.upper()
        }
        if environ:
            env.update(environ)

        def start_response(status, headers):
            response.write(b'%s\n' % status.encode())
            for k, v in headers:
                response.write(b'%s:%s\n' % (k.encode(), v.encode()))

        for i in app(env, start_response):
            response.write(i.encode())

        return response.getvalue().decode()

    def test_root(self):
        class Root(Controller):

            @action()
            def index(self):
                return 'Index'

        resp = self.serve_app(Root().wsgi_app, '/')
        self.assertEqual(resp, '200 OK\nIndex')


    def test_arguments(self):

        class Root(Controller):

            @action()
            def users(self, user_id, attr=None):
                yield 'User: %s\n' % user_id
                yield 'Attr: %s\n' % attr

        self.assertEqual(self.serve_app(Root().wsgi_app, '/users/10/jobs'), '200 OK\nUser: 10\nAttr: jobs\n')
        self.assertEqual(self.serve_app(Root().wsgi_app, '/users/10/'), '200 OK\nUser: 10\nAttr: \n')
        self.assertEqual(self.serve_app(Root().wsgi_app, '/users/10/11/11'), '404 Not Found\n')



