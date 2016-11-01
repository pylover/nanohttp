from nanohttp import Controller, action
from tests.helpers import WsgiAppTestCase


class HttpHeadersTestCase(WsgiAppTestCase):

    class Root(Controller):

        @action()
        def index(self):
            return 'Index'

        @action(content_type=None)
        def no_content_type(self):
            return 'No Content Type'

        @action(content_type='text/html')
        def html(self):
            return 'Html'


    def test_response_header(self):
        self.assert_get('/', expected_headers={'Content-Type': 'text/plain'})
        self.assert_get('/html', expected_headers={'Content-Type': 'text/html'})
        self.assert_get('/no_content_type', not_expected_headers=['Content-Type'])
