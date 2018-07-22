import unittest
import re

from nanohttp import Controller, action, text, html, context, chunked_encoding
from nanohttp.tests.helpers import WsgiAppTestCase


class ChunkedEncodingTestCase(WsgiAppTestCase):

    class Root(Controller):

        @chunked_encoding(trailer={'Field': 'value'})
        @text
        def trailer(self):
            yield 'This'
            yield 'is'
            yield 'test'

        @chunked_encoding()
        @text
        def chunked(self):
            yield 'This'
            yield 'is'
            yield 'test'

    def test_chunked_encoding(self):
        ___, response = self.assert_get(
            '/trailer',
            expected_headers={
                'Trailer': 'Field',
                'transfer-encoding': 'chunked'
            }
        )
        self.assertEqual(response, b'Thisistest')


    def test_http_trailler(self):
        ___, response = self.assert_get(
            '/chunked',
            expected_headers={
                'transfer-encoding': 'chunked'
            }
        )
        self.assertEqual(response, b'Thisistest')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
