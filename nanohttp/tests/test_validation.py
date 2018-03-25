import unittest
import re

from nanohttp import HttpBadRequest

from nanohttp.validation import ActionValidator


class ValidationTestCase(unittest.TestCase):

    def test_validation_required(self):

        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    required=True
                )
            )
        )
        self.assertEqual(dict(param1='value1'), validator(dict(param1='value1')))

        # Missing parameter
        with self.assertRaises(HttpBadRequest):
            validator({})

    def test_validation_max(self):

        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    max=10
                )
            )
        )
        self.assertEqual(dict(param1=9), validator(dict(param1=9)))
        self.assertEqual(dict(param1=9), validator(dict(param1='9')))

        # More than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1=11))

    def test_validation_min(self):

        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    min=10
                )
            )
        )

        self.assertEqual(dict(param1=11), validator(dict(param1=11)))
        self.assertEqual(dict(param1=11), validator(dict(param1='11')))

        # Less than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1=9))

    def test_validation_min_length(self):

        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    min_length=3
                )
            )
        )
        self.assertEqual(dict(param1='abcd'), validator(dict(param1='abcd')))
        self.assertEqual(dict(param1='abc'), validator(dict(param1='abc')))
        self.assertEqual(dict(param1='1234'), validator(dict(param1=1234)))

        # Shorter than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='ab'))

    def test_validation_max_length(self):
        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    max_length=4
                )
            )
        )
        self.assertEqual(dict(param1='abc'), validator(dict(param1='abc')))
        self.assertEqual(dict(param1='abcd'), validator(dict(param1='abcd')))
        self.assertEqual(dict(param1='1234'), validator(dict(param1=1234)))

        # Longer than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='abbcde'))

    def test_validation_pattern(self):
        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    pattern='^\D{10}$'
                )
            )
        )

        self.assertEqual(dict(param1='abcdeFGHIJ'), validator(dict(param1='abcdeFGHIJ')))

        # Param1 not matching
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='asc'))

    def test_validation_pattern_compiled(self):
        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    pattern=re.compile(r'^\d{10}$')
                )
            )
        )

        self.assertEqual(
            dict(param1='0123456789'), validator(dict(param1='0123456789'))
        )

        # Param1 not matching
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='12345'))

    def test_validation_type(self):
        validator = ActionValidator(
            fields=dict(
                param1=dict(
                    type=int
                ),
                param2=dict(
                    type=str
                )
            )
        )

        self.assertEqual(
            dict(param1=123, param2='123'), validator(dict(param1='123', param2=123))
        )

        # Param1 bad value(Cannot be converted to int)
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='str', param2='str'))


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
