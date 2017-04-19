from nanohttp import Controller, action, text, HttpMovedPermanently, HttpFound
from nanohttp.tests.helpers import WsgiAppTestCase


class HttpRedirectTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text()
        def index(self):
            raise HttpMovedPermanently('/new/address')

        @action()
        def about(self):
            raise HttpFound('/new/address')

    def test_redirect_response_header(self):
        self.assert_get('/', status=301, expected_headers={'Location': '/new/address'})
        self.assert_get('/about', status=302, expected_headers={'Location': '/new/address'})

