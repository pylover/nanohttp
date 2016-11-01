

from nanohttp.tests.helpers import WsgiAppTestCase
from nanohttp import Controller, action, context


class QueryStringTestCase(WsgiAppTestCase):


    class Root(Controller):

        @action()
        def index(self):
            return ', '.join('%s: %s' % (k, v) for k, v in sorted(context.query_string.items(), key=lambda x: x[0]))


    def test_simple_query_string(self):
        self.assert_get('/?a=1&b=&c=2', "a: 1, b: , c: 2")
        self.assert_get('/?a=1&b=2', "a: 1, b: 2")
        self.assert_get('/?a=1&b=2&b=3', "a: 1, b: ['2', '3']")
        self.assert_get('/', query_string=dict(a=1, b=2), resp="a: 1, b: 2")

