import unittest

from nanohttp.helpers import LazyAttribute


class LazyAttributeTestCase(unittest.TestCase):
    def test_wrapping(self):

        class O:
            @LazyAttribute
            def attr1(self):
                """Attribute 1"""
                return 1

        self.assertEqual('Attribute 1', O.attr1.__doc__)
        self.assertEqual('attr1', O.attr1.__name__)

        o = O()
        self.assertEqual(1, o.attr1)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()

