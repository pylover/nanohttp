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
    @chunked_encoding({'key': 'value'})
    def trailer():
        yield 'first chunk'
        yield 'second chunk'


    @staticmethod
    @chunked_encoding({'key': 'value'})
    def error():
        yield 'first chunk'
        yield 1/0
        yield 'third chunk'


    def test_chunked_encoding(self):

        output_generator = self.chunked()
        expected_chunks = [
            '11\r\nfirst chunk\r\n',
            '12\r\nsecond chunk\r\n',
            '11\r\nthird chunk\r\n',
            '0\r\n',
            '\r\n',
        ]
        with Context(environ={}) as context:
            range_index = 0
            for chunk in output_generator:
                self.assertEqual(chunk, expected_chunks[range_index])
                range_index += 1

            self.assertEqual(
                context.response_headers['transfer-encoding'], 'chunked'
            )


    def test_trailer(self):

        output_generator = self.trailer()
        expected_chunks = [
            '11\r\nfirst chunk\r\n',
            '12\r\nsecond chunk\r\n',
            '0\r\n',
            'key: value\r\n',
            '\r\n',
        ]
        with Context(environ={}) as context:
            range_index = 0
            for chunk in output_generator:
                self.assertEqual(chunk, expected_chunks[range_index])
                range_index += 1

            self.assertEqual(context.response_headers['trailer'], 'key')


    def test_error(self):

        output_generator = self.error()
        expected_chunks = [
            '11\r\nfirst chunk\r\n',
            'division by zero',
            '0\r\n',
            '\r\n',
        ]
        with Context(environ={}) as context:
            range_index = 0
            for chunk in output_generator:
                self.assertEqual(chunk, expected_chunks[range_index])
                range_index += 1


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

