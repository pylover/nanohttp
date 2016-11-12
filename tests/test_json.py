
import ujson

from nanohttp import Controller, json
from tests.helpers import WsgiAppTestCase


class JsonTestCase(WsgiAppTestCase):

    class Root(Controller):

        @json
        def index(self):
            return {
                'a': 1,
                'b': '2'
            }

    def test_json(self):
        resp, content = self.assert_get(
            '/',
            status=200,
            expected_headers={'content-type': 'application/json; charset=utf-8'},
        )
        self.assertDictEqual(ujson.loads(content), {'b': '2', 'a': 1})
