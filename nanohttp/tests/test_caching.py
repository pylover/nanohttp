import unittest

from nanohttp import Controller, text, must_revalidate
from nanohttp.tests.helpers import WsgiAppTestCase


_etag = '1'


class CachingTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        @must_revalidate(etag=lambda: _etag)
        def index(self):
            yield 'Something'

        @text()
        def about(self):
            yield 'about'

    def test_caching_header(self):
        global _etag
        self.assert_get('/', expected_headers={'Cache-Control': 'must-revalidate', 'ETag': _etag})

        # Fetching again with etag header
        ___, body = self.assert_get('/', headers={'If-None-Match': _etag}, status=304)
        self.assertEqual(len(body), 0)

        _old_etag = _etag
        _etag = '2'
        # Fetching again with etag header
        ___, body = self.assert_get(
            '/',
            headers={'If-None-Match': _old_etag},
            status=200,
            expected_headers={'Cache-Control': 'must-revalidate', 'ETag': _etag}
        )
        self.assertEqual(body, b'Something')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
