from nanohttp import Controller, action, text, html, HttpMovedPermanently, HttpFound
from tests.helpers import WsgiAppTestCase


class HttpHeadersTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        def index(self):
            raise HttpMovedPermanently('/html')

        @action()
        def about(self):
            raise HttpFound('/html')

        @html()
        def html(self):
            return 'Html'


    def test_redirect_response_header(self):
        self.assert_get('/', status=301, expected_headers={'Location': '/html'})
        self.assert_get('/about', status=302, expected_headers={'Location': '/html'})

