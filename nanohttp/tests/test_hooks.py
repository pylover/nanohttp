
import unittest

from nanohttp import Controller, text, context, Application
from nanohttp.tests.helpers import WsgiAppTestCase


class HooksTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        def index(self):
            yield 'Index'

    class Application(Application):

        @classmethod
        def begin_response(cls):
            context.response_headers.add_header('my-header', 'dummy')

    def test_hooks(self):
        self.assert_get('/', expected_headers={'my-header': 'dummy'})


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
