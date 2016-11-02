
import unittest
from os.path import join

# noinspection PyProtectedMember
from nanohttp import _load_controller_from_file
from tests.helpers import TEST_DIR


class BootstrapTestCase(unittest.TestCase):

    def test_load_controller_from_file(self):
        controller = _load_controller_from_file('nanohttp:Static', join(TEST_DIR, '..'))
        self.assertIsNotNone(controller)
        self.assertTrue(hasattr(controller, 'load_app'))

        controller = _load_controller_from_file('nanohttp.py:Static', join(TEST_DIR, '..'))
        self.assertIsNotNone(controller)
        self.assertTrue(hasattr(controller, 'load_app'))
