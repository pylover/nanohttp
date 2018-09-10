
import unittest

from nanohttp import html, RestController
from nanohttp.tests.helpers import WsgiAppTestCase


class RestDispatcherTestCase(WsgiAppTestCase):

    class Root(RestController):

        @html
        def get(self, article_id: int = None):
            yield "GET Article%s" % (
                's' if not article_id else (': ' + article_id)
            )

        @html
        def post(self):
            yield "POST Article"

        @html
        def put(self, article_id: int = None):
            yield "PUT Article: %s" % article_id

        def disallowed(self):  # pragma: nocover
            yield 'bad'

    def test_verbs(self):
        self.assert_get('/', expected_response='GET Articles')
        self.assert_post('/', expected_response='POST Article')
        self.assert_put('/12', expected_response='PUT Article: 12')
        self.assert_get('/disallowed', status=404)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
