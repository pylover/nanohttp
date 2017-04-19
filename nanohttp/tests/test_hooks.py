

from nanohttp import Controller, text, context
from nanohttp.tests.helpers import WsgiAppTestCase


class HooksTestCase(WsgiAppTestCase):

    class Root(Controller):

        @classmethod
        def begin_response(cls):
            context.response_headers.add_header('my-header', 'dummy')

        @text()
        def index(self):
            yield 'Index'

    def test_hooks(self):
        self.assert_get('/', expected_headers={'my-header': 'dummy'})
