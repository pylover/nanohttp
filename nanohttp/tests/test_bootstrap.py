
import unittest
from os.path import join

# noinspection PyProtectedMember
from nanohttp.helpers import load_controller_from_file
from nanohttp.tests.helpers import TEST_DIR


class BootstrapTestCase(unittest.TestCase):

    def test_load_controller_from_file(self):
        controller = load_controller_from_file(':Static')
        self.assertIsNotNone(controller)

        controller = load_controller_from_file(join(TEST_DIR, 'stuff', 'package_for_test_bootstrapping'))
        self.assertIsNotNone(controller)

        controller = load_controller_from_file(join(TEST_DIR, 'stuff', 'module_for_test_bootstrapping.py'))
        self.assertIsNotNone(controller)

        controller = load_controller_from_file(join(TEST_DIR, 'stuff', 'module_for_test_bootstrapping'))
        self.assertIsNotNone(controller)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
