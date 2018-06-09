
import unittest

from nanohttp import Controller, html, HttpBadRequest, json, HttpStatus
from nanohttp.tests.helpers import WsgiAppTestCase


class ExceptionTestCase(WsgiAppTestCase):

    class Root(Controller):
        @html
        def index(self):
            raise HttpBadRequest()

        @json
        def data(self):
            raise HttpBadRequest()

        @json
        def custom(self):
            raise HttpStatus(status='462 custom text')

        @html
        def err(self):
            x = 1 / 0
            return 'test'

    def test_exception(self):
        self.assert_get('/', status=400)

        self.assert_get('/data', status=400)

        # @Arash Fatahzade Consider this while changing
        # self.assertDictEqual(ujson.loads(content), {
        #     'description': 'Bad request syntax or unsupported method',
        # })

        response, content = self.assert_get('/err', status=500)
        self.assertIsNotNone(content)

    def test_custom_exception(self):
        self.assert_get('/custom', status=462)

        # @Arash Fatahzade Consider this while changing
        # self.assertDictEqual(ujson.loads(content), {
        #     'description': 'custom info',
        # })


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
