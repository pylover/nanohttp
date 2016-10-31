
import unittest

from nanohttp.tests.helpers import WsgiTester
from nanohttp import Controller, action


class WsgiAppTestCase(unittest.TestCase):

    class Root(Controller):
        pass

    def setUp(self):
        self.client = WsgiTester(self.Root().load_app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)

    def assert_get(self, uri, resp=None, status=200):
        response, content = self.client.get(uri)
        self.assertEqual(response.status, status)
        if resp is not None:
            self.assertEqual(content.decode(), resp)
        return response, content


class DispatcherTestCase(WsgiAppTestCase):

    class Root(Controller):
        @action()
        def users(self, user_id, attr=None):
            yield 'User: %s\n' % user_id
            yield 'Attr: %s\n' % attr

        @action()
        def index(self, *args, **kw):
            yield 'Index'

    def test_root(self):
        self.assert_get('/', 'Index')

    def test_arguments(self):
        self.assert_get('/users/10/jobs', 'User: 10\nAttr: jobs\n')
        self.assert_get('/users/10/', 'User: 10\nAttr: \n')
        self.assert_get('/users/10/11/11', status=404)



