import unittest
import time

from nanohttp.helpers import LazyAttribute


class LazyAttributeTestCase(unittest.TestCase):
    def test_wrapping(self):

        class O:
            @LazyAttribute
            def attr1(self):
                """Attribute 1"""
                return time.time()

        self.assertEqual('Attribute 1', O.attr1.__doc__)
        self.assertEqual('attr1', O.attr1.__name__)


if __name__ == '__main__':
    unittest.main()

