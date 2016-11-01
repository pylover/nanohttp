from os.path import join

from nanohttp import Controller, action, Static
from tests.helpers import WsgiAppTestCase, STUFF_DIR, md5sum


CAT = join(STUFF_DIR, 'cat.jpg')


class StaticFileTestCase(WsgiAppTestCase):

    class Root(Controller):
        cat = Static(CAT)
        static = Static(STUFF_DIR)

        @action()
        def index(self):
            yield 'Index'

    def test_simple_query_string(self):
        checksum = md5sum(CAT)
        self.assert_get('/cat', expected_checksum=checksum)
        self.assert_get('/static/cat.jpg', expected_checksum=checksum)
