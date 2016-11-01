import re

from nanohttp import Controller, action, HttpForbidden
from tests.helpers import WsgiAppTestCase


class DispatcherTestCase(WsgiAppTestCase):


    class Root(Controller):

        class Links(Controller):

            class Promotions(Controller):

                @action()
                def index(self):
                    yield 'Promotions index'

                @action()
                def select(self, id):
                    yield 'Selection promotion: %s' % id

            promos = Promotions()

            @action()
            def index(self):
                yield 'Links index'

            @action()
            def add(self, link):
                yield 'Adding link: %s' % link

        links = Links()

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
        self.assert_get('/bad', resp=re.compile('.*Exception.*'), status=500)

    def test_nested(self):
        self.assert_get('/links', 'Links index')
        self.assert_get('/links/add/mylink', 'Adding link: mylink')
        self.assert_get('/links/promos/', 'Promotions index')
        self.assert_get('/links/promos/select/1', 'Selection promotion: 1')
