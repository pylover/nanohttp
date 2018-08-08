import unittest
import re

from nanohttp import Controller, action, text, html, context, chunked
from nanohttp.contexts import Context
from nanohttp.tests.helpers import WsgiAppTestCase


class ChunkedEncodingTestCase(WsgiAppTestCase):


    @staticmethod
    @chunked
    def chunked_action():
        yield 'first chunk'
        yield 'second chunk'
        yield 'third chunk'

    @staticmethod
    @chunked('field', 'value')
    def trailer_action():
        yield 'first chunk'
        yield 'second chunk'

    @staticmethod
    @chunked('field', 'value')
    def error_action():
        yield 'first chunk'
        yield 1/0
        yield 'third chunk'

    def test_chunked(self):
        output_generator = self.chunked_action()
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
        output_generator = self.trailer_action()
        with Context(environ={}) as context:
            self.assertEqual(next(output_generator), '11\r\nfirst chunk\r\n')
            self.assertEqual(next(output_generator), '12\r\nsecond chunk\r\n')
            self.assertEqual(next(output_generator), '0\r\n')
            self.assertEqual(next(output_generator), 'field: value\r\n')
            self.assertEqual(next(output_generator), '\r\n')
            self.assertEqual(context.response_headers['trailer'], 'field')

    def test_error(self):
        output_generator = self.error_action()
        with Context(environ={}) as context:
            self.assertEqual(next(output_generator), '11\r\nfirst chunk\r\n')
            self.assertEqual(next(output_generator), 'division by zero')
            self.assertEqual(next(output_generator), '0\r\n')
            self.assertEqual(next(output_generator), '\r\n')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

