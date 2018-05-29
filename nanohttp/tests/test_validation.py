import unittest
import re

from nanohttp import HttpBadRequest, HttpStatus, Controller, action, validate
from nanohttp.tests.helpers import WsgiAppTestCase
from nanohttp.validation import RequestValidator


class ValidationTestCase(unittest.TestCase):

    def test_validation_required(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(required=True)
            )
        )
        self.assertEqual(
            (dict(param1='value1'), None),
            validator(dict(param1='value1'))
        )

        # Missing param1
        with self.assertRaises(HttpBadRequest):
            validator(dict(anotherParam1='value1'))

        # Required false
        validator = RequestValidator(
            fields=dict(
                param1=dict(required=False)
            )
        )

        # Send another param
        self.assertEqual(
            (dict(another_param='value'), None),
            validator(dict(another_param='value'))
        )

    def test_validation_max(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(maximum=10)
            )
        )
        self.assertEqual((dict(param1=9), None), validator(dict(param1=9)))
        self.assertEqual(
            (dict(param1=None), None),
            validator(dict(param1=None))
        )
        with self.assertRaises(HttpBadRequest):
            self.assertEqual(
                (dict(param1=9), None),
                validator(dict(param1='9'))
            )

        # More than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1=11))

        # Not int input
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='a'))

    def test_validation_min(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(minimum=10)
            )
        )

        self.assertEqual((dict(param1=11), None), validator(dict(param1=11)))
        with self.assertRaises(HttpBadRequest):
            self.assertEqual(
                (dict(param1=11), None),
                validator(dict(param1='11'))
            )

        # Less than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1=9))

    def test_validation_min_length(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(min_length=3)
            )
        )
        self.assertEqual(
            (dict(param1='abcd'), None),
            validator(dict(param1='abcd'))
        )
        self.assertEqual(
            (dict(param1='abc'), None),
            validator(dict(param1='abc'))
        )
        self.assertEqual(
            (dict(param1='1234'), None),
            validator(dict(param1=1234))
        )

        # Shorter than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='ab'))

    def test_validation_max_length(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(max_length=4)
            )
        )
        self.assertEqual(
            (dict(param1='abc'), None),
            validator(dict(param1='abc'))
        )
        self.assertEqual(
            (dict(param1='abcd'), None),
            validator(dict(param1='abcd'))
        )
        self.assertEqual(
            (dict(param1='1234'), None),
            validator(dict(param1=1234))
        )

        # Longer than Expectation
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='abbcde'))

    def test_validation_pattern(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(pattern='^\D{10}$')
            )
        )

        self.assertEqual(
            (dict(param1='abcdeFGHIJ'), None),
            validator(dict(param1='abcdeFGHIJ'))
        )

        # Param1 not matching
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='asc'))

    def test_validation_pattern_compiled(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(pattern=re.compile(r'^\d{10}$'))
            )
        )

        self.assertEqual(
            (dict(param1='0123456789'), None),
            validator(dict(param1='0123456789'))
        )

        # Param1 not matching
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='12345'))

    def test_validation_type(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(type_=int),
                param2=dict(type_=str)
            )
        )

        self.assertEqual(
            (dict(param1=123, param2='123'), None),
            validator(dict(param1='123', param2=123))
        )

        # Param1 bad value(Cannot be converted to int)
        with self.assertRaises(HttpBadRequest):
            validator(dict(param1='NotInteger', param2='NotInteger'))

    def test_validation_query_string(self):

        # Accept query_string
        validator = RequestValidator(
            fields=dict(
                param1=dict(query_string=True),
            )
        )

        self.assertEqual(
            (None, dict(param1='value')),
            validator(query_string=dict(param1='value'))
        )

    def test_validation_custom_status(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(
                    type_=(int, '999 Type error'),
                    minimum=(30, '666')
                )
            )
        )

        try:
            validator(dict(param1='NotInteger'))
        except HttpStatus as e:
            self.assertEqual(e.status_code, 999)
            self.assertEqual(e.status_text, 'Type error')

        try:
            validator(dict(param1=29))
        except HttpStatus as e:
            self.assertEqual(e.status_code, 666)
            self.assertEqual(e.status_text, 'Bad request')


class ValidationDecoratorTestCase(WsgiAppTestCase):
    class Root(Controller):

        @validate(
            param1=dict(
                required=True
            )
        )
        @action()
        def index(self):
            return ''

    def test_validation_decorator(self):
        self.assert_post('/?param1=1', expected_response='')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
