
import unittest
from os.path import join, abspath

# noinspection PyProtectedMember
from nanohttp.helpers import load_controller_from_file
from tests.helpers import TEST_DIR


class BootstrapTestCase(unittest.TestCase):

    def test_load_controller_from_file(self):
        controller = load_controller_from_file(':Static')
        self.assertIsNotNone(controller)
        self.assertTrue(hasattr(controller, 'load_app'))

        controller = load_controller_from_file(join(TEST_DIR, 'stuff', 'package_for_test_bootstrapping'))
        self.assertIsNotNone(controller)
        self.assertTrue(hasattr(controller, 'load_app'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

