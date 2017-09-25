from os.path import join

from nanohttp import Controller, Static
from nanohttp.tests.helpers import WsgiAppTestCase, STUFF_DIR, md5sum

CAT = join(STUFF_DIR, 'cat.jpg')


class StaticFileTestCase(WsgiAppTestCase):

    class Root(Controller):
        cat = Static(CAT)
        static = Static(STUFF_DIR)
        assets = Static(STUFF_DIR, default_document=None)

    def test_static_file(self):
        checksum = md5sum(CAT)
        self.assert_get('/cat', expected_checksum=checksum)
        self.assert_get('/static/cat.jpg', expected_checksum=checksum)
        self.assert_get('/static', status=403)
        self.assert_get('/static/not-exists', status=404)
        self.assert_get('/static/..', status=403)
        self.assert_get('/assets/', status=403)
