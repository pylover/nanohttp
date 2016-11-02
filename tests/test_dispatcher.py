import re

from nanohttp import Controller, action, HttpForbidden
from tests.helpers import WsgiAppTestCase


class DispatcherTestCase(WsgiAppTestCase):


    class Root(Controller):

        class Links(Controller):

            class Promotions(Controller):

                @action
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

        @action(methods='get')
        def index(self, *args, **kw):
            yield 'Index'

        @action()
        def bad(self):
            raise Exception

    def test_root(self):
        self.assert_get('/', 'Index')

    def test_arguments(self):
        self.assert_get('/users/10/jobs', expected_response='User: 10\nAttr: jobs\n')
        self.assert_get('/users/10/', expected_response='User: 10\nAttr: \n')
        self.assert_get('/users/10/11/11', status=404)

    def test_exception(self):
        self.assert_get('/bad', expected_response=re.compile('.*Exception.*'), status=500)
        self.assert_post('/', status=405)

    def test_nested(self):
        self.assert_get('/links', expected_response='Links index')
        self.assert_get('/links/add/mylink', expected_response='Adding link: mylink')
        self.assert_get('/links/promos/', expected_response='Promotions index')
        self.assert_get('/links/promos/select/1', expected_response='Selection promotion: 1')
