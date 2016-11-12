import time

from nanohttp import Controller, text, quickstart
from tests.helpers import WsgiAppTestCase, find_free_tcp_port


class QuickstartTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text
        def index(self):
            yield 'Index'

    def setUp(self):
        super().setUp()
        self.port = find_free_tcp_port()

    def test_without_controller(self):
        shutdown = quickstart(port=self.port, block=False)
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()

    def test_with_controller(self):
        shutdown = quickstart(controller=self.Root(), block=False, port=self.port)
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()




