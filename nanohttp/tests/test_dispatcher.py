
from nanohttp.tests.helpers import WsgiAppTestCase
from nanohttp import Controller, action, HttpForbidden


class DispatcherTestCase(WsgiAppTestCase):

    class Root(Controller):
        @action()
        def users(self, user_id, attr=None):
            yield 'User: %s\n' % user_id
            yield 'Attr: %s\n' % attr

        @action()
        def index(self, *args, **kw):
            yield 'Index'

        @action()
        def not_forbidden(self):
            raise HttpForbidden()

        @action()
        def bad(self):
            raise Exception

    def test_root(self):
        self.assert_get('/', 'Index')

    def test_arguments(self):
        self.assert_get('/users/10/jobs', 'User: 10\nAttr: jobs\n')
        self.assert_get('/users/10/', 'User: 10\nAttr: \n')
        self.assert_get('/users/10/11/11', status=404)

    def test_exception(self):
        self.assert_get('/bad', resp='.*Exception.*', status=500)
