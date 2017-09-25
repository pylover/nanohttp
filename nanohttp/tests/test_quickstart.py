import time
import unittest

from nanohttp import Controller, quickstart, settings
from nanohttp.tests.helpers import WsgiAppTestCase, find_free_tcp_port


class QuickstartTestCase(WsgiAppTestCase):

    class Root(Controller):
        pass

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

    def test_with_application(self):
        shutdown = quickstart(application=self.application, block=False, port=self.port)
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()

    def test_before_configure(self):
        settings.__class__._set_instance(None)
        shutdown = quickstart(
            port=self.port,
            block=False,
            config='''
            test_config_item: item1
            '''
        )
        self.assertTrue(callable(shutdown))
        time.sleep(.5)
        shutdown()


if __name__ == '__main__':  # pragma: no cover
    unittest.main()



