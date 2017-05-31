
import unittest

import ujson

from nanohttp import Controller, html, HttpBadRequest, json
from nanohttp.tests.helpers import WsgiAppTestCase


class ExceptionTestCase(WsgiAppTestCase):

    class Root(Controller):
        @html
        def index(self):
            raise HttpBadRequest(reason='blah blah')

        @json
        def data(self):
            raise HttpBadRequest(reason='blah blah')

        @html
        def err(self):
            x = 1 / 0
            return 'test'

    def test_reason(self):
        response, content = self.assert_get('/', status=400)
        self.assertIn('x-reason', response)
        self.assertEqual(response['x-reason'], 'blah blah')
        
        response, content = self.assert_get('/data', status=400)
        self.assertIn('x-reason', response)
        self.assertEqual(response['x-reason'], 'blah blah')
        self.assertDictEqual(ujson.loads(content), {
            'description': 'Bad request syntax or unsupported method',
            'message': 'Bad Request'
        })

        response, content = self.assert_get('/err', status=500)
        self.assertEqual(content, b'Internal server error.')
        self.assertEqual(response.reason, b'Internal server error.')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
