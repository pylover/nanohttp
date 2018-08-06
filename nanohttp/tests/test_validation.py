import re
import unittest
from decimal import Decimal

from nanohttp import HTTPBadRequest, HTTPStatus, Controller, action, validate
from nanohttp.tests.helpers import WsgiAppTestCase
from nanohttp.validation import RequestValidator


def custom_validation(input_string):
    expected_string = 'A sample string'
    if input_string is not expected_string:
        return False
    return True


class ValidationTestCase(unittest.TestCase):

    def test_validation_required(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(required=True)
            )
        )

        # Trying to pass with param1
        self.assertEqual(
            (dict(param1='value1'), None),
            validator(dict(param1='value1'))
        )

        # Trying to pass without param1
        with self.assertRaises(HTTPBadRequest):
            validator(dict(another_param='value1'))

        # Define required validation with custom exception
        validator = RequestValidator(
            fields=dict(
                param1=dict(required='600 Custom exception')
            )
        )

        # Trying to pass with another param without param1
        with self.assertRaises(HTTPStatus('600 Custom exception').__class__):
            validator(dict(another_param='value1'))

        # Trying to pass with param1
        self.assertEqual(
            (dict(param1='value1'), None),
            validator(dict(param1='value1'))
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
        with self.assertRaises(HTTPBadRequest):
            self.assertEqual(
                (dict(param1=9), None),
                validator(dict(param1='9'))
            )

        # More than Expectation
        with self.assertRaises(HTTPBadRequest):
            validator(dict(param1=11))

        # Not int input
        with self.assertRaises(HTTPBadRequest):
            validator(dict(param1='a'))

    def test_validation_min(self):

        validator = RequestValidator(
            fields=dict(
                param1=dict(minimum=10)
            )
        )

        self.assertEqual((dict(param1=11), None), validator(dict(param1=11)))
        with self.assertRaises(HTTPBadRequest):
            self.assertEqual(
                (dict(param1=11), None),
                validator(dict(param1='11'))
            )

        # Less than Expectation
        with self.assertRaises(HTTPBadRequest):
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
        with self.assertRaises(HTTPBadRequest):
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
        with self.assertRaises(HTTPBadRequest):
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
        with self.assertRaises(HTTPBadRequest):
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
        with self.assertRaises(HTTPBadRequest):
            validator(dict(param1='12345'))

    def test_validation_type(self):
        validator = RequestValidator(
            fields=dict(
                param1=dict(type_=int),
                param2=dict(type_=str),
                param3=dict(type_=Decimal)
            )
        )

        self.assertEqual(
            (dict(param1=123, param2='123', param3=1.23), None),
            validator(dict(param1='123', param2=123, param3=1.23))
        )

        # Param1 bad value(Cannot be converted to int)
        with self.assertRaises(HTTPBadRequest):
            validator(
                dict(
                    param1='NotInteger',
                    param2='NotInteger',
                    param3='NotInteger'
                )
            )

        # Param3 bad value(Cannot be converted to decimal)
        with self.assertRaises(HTTPBadRequest):
            validator(
                dict(param1=1, param2='str', param3='NotDecimal'))

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
                    minimum=(30, '666'),
                    maximum=(40, '400 greater than maximum'),
                )
            )
        )

        try:
            validator(dict(param1='NotInteger'))
        except HTTPStatus as e:
            self.assertEqual(e.status, '999 Type error')

        try:
            validator(dict(param1=29))
        except HTTPStatus as e:
            self.assertEqual(e.status, '666 Bad request')

        try:
            validator(dict(param1=41))
        except HTTPStatus as e:
            self.assertEqual(e.status, '400 greater than maximum')

    def test_callable_validator(self):
        def f(age, container, field):
            age = int(age)
            if age < 0:
                raise ValueError('Age is not in valid range')
            return age

        validator = RequestValidator(
            fields=dict(
                param1=f
            )
        )

        with self.assertRaises(ValueError):
            validator(dict(param1=-1))

        self.assertEqual(
            dict(param1=12).items(),
            validator(dict(param1=12))[0].items()
        )

    def test_not_none_validator(self):
        validator = RequestValidator(fields=dict(param1=dict(not_none=True)))
        with self.assertRaises(HTTPBadRequest):
            validator(dict(param1=None))

        validator = RequestValidator(
            fields=dict(param1=dict(not_none='666 param1 is null'))
        )
        with self.assertRaises(HTTPStatus) as ctx:
            validator(dict(param1=None))
        exception = ctx.exception
        self.assertEqual('666 param1 is null', str(exception))


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
