import unittest

from nanohttp import Controller, text, ifmatch, etag
from nanohttp.tests.helpers import WsgiAppTestCase


_etag = '1'


class CachingTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        @etag(tag=lambda: _etag)
        def index(self):
            yield 'Something'

        @text(verbs='put')
        @ifmatch(tag=lambda: _etag)
        def about(self):
            yield 'About is Modified'

    def test_if_none_match_header(self):
        global _etag
        _etag = '1'

        self.assert_get('/', expected_headers={'Cache-Control': 'must-revalidate', 'ETag': _etag})

        # Fetching again with etag header
        ___, body = self.assert_get('/', headers={'If-None-Match': _etag}, status=304)
        self.assertEqual(len(body), 0)

        _old_etag = _etag
        _etag = '2'
        # Fetching with If-None-Match header
        ___, body = self.assert_get(
            '/',
            headers={'If-None-Match': _old_etag},
            status=200,
            expected_headers={'Cache-Control': 'must-revalidate', 'ETag': _etag}
        )
        self.assertEqual(body, b'Something')

    def test_if_match_header(self):
        global _etag
        _etag = '1'

        # Putting without the header
        self.assert_put('/about', status=412)

        # Putting with expired If-Match header
        _old_etag = _etag
        _etag = '2'
        self.assert_put('/about', headers={'If-Match': _old_etag}, status=412)

        # Putting with valid If-Match header
        ___, body = self.assert_put(
            '/about',
            headers={'If-Match': _etag},
            status=200,
            expected_headers={'Cache-Control': 'must-revalidate', 'ETag': _etag}
        )
        self.assertEqual(body, b'About is Modified')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
