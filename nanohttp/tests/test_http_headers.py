
import unittest
import re

from nanohttp import Controller, action, text, html, context
from nanohttp.tests.helpers import WsgiAppTestCase


class HttpHeadersTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        def index(self):
            yield 'Index'

        @action()
        def no_content_type(self):
            yield'No Content Type'

        @html()
        def html(self):
            yield context.response_content_type

        @action
        def custom_header(self):
            import time
            context.response_headers.add_header('my-header',  str(time.time()))
            yield ''

    def test_response_header(self):
        self.assert_get('/', expected_headers={'Content-Type': 'text/plain; charset=utf-8'})
        self.assert_get('/html', expected_headers={'Content-Type': 'text/html; charset=utf-8'})
        self.assert_get('/no_content_type', not_expected_headers=['Content-Type'])
        self.assert_get('/custom_header', expected_headers={
            'my-header': re. compile('\d+.?\d*')
        })


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
