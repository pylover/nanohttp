import time

from nanohttp import Controller, text, quickstart
from tests.helpers import WsgiAppTestCase


class QuickstartTestCase(WsgiAppTestCase):

    class Root(Controller):

        @text
        def index(self):
            yield 'Index'

    def test_without_controller(self):
        shutdown = quickstart(block=False)
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()

    def test_with_controller(self):
        shutdown = quickstart(controller=self.Root(), block=False)
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()




