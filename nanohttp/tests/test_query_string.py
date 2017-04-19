import unittest

from nanohttp import Controller, action, context, RestController
from nanohttp.tests.helpers import WsgiAppTestCase


class Users(RestController):
    @action
    def post(self):
        return ', '.join('%s: %s' % (k, v) for k, v in sorted(context.query_string.items(), key=lambda x: x[0]))


class QueryStringTestCase(WsgiAppTestCase):

    class Root(Controller):
        users = Users()

        @action()
        def index(self):
            return ', '.join('%s: %s' % (k, v) for k, v in sorted(context.query_string.items(), key=lambda x: x[0]))

    def test_simple_query_string(self):
        self.assert_get('/?a=1&b=&c=2', expected_response="a: 1, b: , c: 2")
        self.assert_get('/?a=1&b=2', expected_response="a: 1, b: 2")
        self.assert_get('/?a=1&b=2&b=3', expected_response="a: 1, b: ['2', '3']")
        self.assert_get('/', query_string=dict(a=1, b=2), expected_response="a: 1, b: 2")
        self.assert_post('/', query_string=dict(a=1, b=2), expected_response="a: 1, b: 2")

    def test_rest_controller_query_string(self):
        self.assert_post('/users', query_string=dict(a=1, b=2), expected_response="a: 1, b: 2")


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
