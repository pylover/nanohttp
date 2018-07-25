import unittest
import re

from nanohttp import Controller, action, text, html, context, chunked_encoding
from nanohttp.contexts import Context
from nanohttp.tests.helpers import WsgiAppTestCase


class ChunkedEncodingTestCase(WsgiAppTestCase):

    @staticmethod
    @chunked_encoding
    def chunked():
        yield 'first chunk'
        yield 'second chunk'
        yield 'third chunk'

    @staticmethod
    @chunked_encoding({'field': 'value'})
    def trailer():
        yield 'first chunk'
        yield 'second chunk'

    @staticmethod
    @chunked_encoding({'field': 'value'})
    def error():
        yield 'first chunk'
        yield 1/0
        yield 'third chunk'

    def test_chunked_encoding(self):
        output_generator = self.chunked()
        with Context(environ={}) as context:
            self.assertEqual(next(output_generator), '11\r\nfirst chunk\r\n')
            self.assertEqual(next(output_generator), '12\r\nsecond chunk\r\n')
            self.assertEqual(next(output_generator), '11\r\nthird chunk\r\n')
            self.assertEqual(next(output_generator), '0\r\n')
            self.assertEqual(next(output_generator), '\r\n')

            self.assertEqual(
                context.response_headers['transfer-encoding'], 'chunked'
            )

    def test_trailer(self):
        output_generator = self.trailer()
        with Context(environ={}) as context:
            self.assertEqual(next(output_generator), '11\r\nfirst chunk\r\n')
            self.assertEqual(next(output_generator), '12\r\nsecond chunk\r\n')
            self.assertEqual(next(output_generator), '0\r\n')
            self.assertEqual(next(output_generator), 'field: value\r\n')
            self.assertEqual(next(output_generator), '\r\n')

            self.assertEqual(context.response_headers['trailer'], 'field')

    def test_error(self):
        output_generator = self.error()
        with Context(environ={}) as context:
            self.assertEqual(next(output_generator), '11\r\nfirst chunk\r\n')
            self.assertEqual(next(output_generator), 'division by zero')
            self.assertEqual(next(output_generator), '0\r\n')
            self.assertEqual(next(output_generator), '\r\n')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

