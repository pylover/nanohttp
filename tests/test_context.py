
import re
import unittest

from nanohttp import Controller, html, ContextIsNotInitializedError, context, Context
from tests.helpers import WsgiAppTestCase


class ContextProxyTestCase(unittest.TestCase):

    def test_context(self):
        self.assertRaises(ContextIsNotInitializedError, Context.get_current)


class ContextTestCase(WsgiAppTestCase):

    class Root(Controller):

        @html
        def get_uri(self):
            yield context.request_uri

        @html
        def get_scheme(self):
            yield context.request_scheme

    def test_redirect_response_header(self):
        self.assert_get(
            '/get_uri',
            query_string={'a': 1, 'b': 2},
            expected_response=re.compile('http://nanohttp.org/get_uri\?[ab=12&]+')
        )

        self.assert_get(
            '/get_scheme',
            expected_response='http'
        )




