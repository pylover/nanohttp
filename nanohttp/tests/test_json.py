
import unittest

import ujson

from nanohttp import Controller, json
from nanohttp.tests.helpers import WsgiAppTestCase


class JsonTestCase(WsgiAppTestCase):

    class Root(Controller):

        @json
        def index(self):
            return {
                'a': 1,
                'b': '2'
            }

        @json
        def via_to_dict(self):
            class Model:
                @staticmethod
                def to_dict():
                    return dict(
                        a=1,
                        b='2'
                    )
            return Model()

        @json
        def error(self):
            class Bad:
                pass
            return Bad()

    def test_json(self):
        resp, content = self.assert_get(
            '/',
            expected_headers={'content-type': 'application/json; charset=utf-8'},
        )
        self.assertDictEqual(ujson.loads(content), {'b': '2', 'a': 1})

        resp, content = self.assert_get('/via_to_dict',)
        self.assertDictEqual(ujson.loads(content), {'b': '2', 'a': 1})

        self.assert_get('/error', status=500)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
