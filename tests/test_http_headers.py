from nanohttp import Controller, action, text, html
from tests.helpers import WsgiAppTestCase


class HttpHeadersTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        def index(self):
            return 'Index'

        @action()
        def no_content_type(self):
            return 'No Content Type'

        @html()
        def html(self):
            return 'Html'


    def test_response_header(self):
        self.assert_get('/', expected_headers={'Content-Type': 'text/plain'})
        self.assert_get('/html', expected_headers={'Content-Type': 'text/html'})
        self.assert_get('/no_content_type', not_expected_headers=['Content-Type'])
