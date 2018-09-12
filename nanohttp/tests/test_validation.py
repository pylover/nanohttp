import re
from decimal import Decimal

import pytest
from nanohttp import RequestValidator, HTTPBadRequest, HTTPStatus, \
    Controller, validate, action, context
from bddrest import status, response

from nanohttp.tests.helpers import Given, when


def test_validation_decorator():
    class Root(Controller):

        @validate(
            query1=dict(
                required=True,
                type_=int,
                query=True
            ),
            field1=dict(
                required=True,
                type_=float
            ),
            field2=dict(
                required=True,
                type_=int
            ),
            field3=dict(
                required=True,
                type_=lambda v: v.encode(),
                min_length=1
            )
        )
        @action
        def index(self):
            query1 = context.query['query1']
            field1 = context.form['field1']
            field2 = context.form['field2']
            field3 = context.form['field3']
            yield \
                f'{type(query1).__name__}: {query1}, '\
                f'{type(field1).__name__}: {field1}, ' \
                f'{type(field2).__name__}: {field2}, ' \
                f'{type(field3).__name__}: {field3}'

    with Given(
        Root(),
        verb='POST',
        query=dict(query1=1),
        form=dict(field1='2.3', field2='2', field3='ab'),
    ):
        assert status == 200
        assert response.text == 'int: 1, float: 2.3, int: 2, bytes: b\'ab\''


def test_validation_required():

    validator = RequestValidator(
        fields=dict(
            a=dict(required=True)
        )
    )

    # Trying to pass with a
    assert dict(a='value1') == validator(dict(a='value1'))[0]

    # Trying to pass without a
    with pytest.raises(HTTPBadRequest):
        validator(dict(another_param='value1'))

    # Define required validation with custom exception
    validator = RequestValidator(
        fields=dict(
            a=dict(required='600 Custom exception')
        )
    )

    # Trying to pass with another param without a
    with pytest.raises(HTTPStatus('600 Custom exception').__class__):
        validator(dict(another_param='value1'))

    # Trying to pass with a
    assert dict(a='value1') == validator(dict(a='value1'))[0]


def test_validation_max():

    validator = RequestValidator(
        fields=dict(
            a=dict(maximum=10)
        )
    )
    assert dict(a=9) == validator(dict(a=9))[0]
    assert dict(a=None) == validator(dict(a=None))[0]

    with pytest.raises(HTTPBadRequest):
         validator(dict(a='9'))

    # More than Expectation
    with pytest.raises(HTTPBadRequest):
        validator(dict(a=11))

    # Not int input
    with pytest.raises(HTTPBadRequest):
        validator(dict(a='a'))


def test_validation_min():

    validator = RequestValidator(
        fields=dict(
            a=dict(minimum=10)
        )
    )

    assert dict(a=11) == validator(dict(a=11))[0]
    with pytest.raises(HTTPBadRequest):
         validator(dict(a='11'))

    # Less than Expectation
    with pytest.raises(HTTPBadRequest):
        validator(dict(a=9))


def test_validation_min_length():

    validator = RequestValidator(
        fields=dict(
            a=dict(min_length=3)
        )
    )
    assert dict(a='abc') == validator(dict(a='abc'))[0]

    # Shorter than Expectation
    with pytest.raises(HTTPBadRequest):
        validator(dict(a='ab'))


def test_validation_max_length():
    validator = RequestValidator(
        fields=dict(
            a=dict(max_length=4)
        )
    )
    assert dict(a='abcd') == validator(dict(a='abcd'))[0]

    # Longer than Expectation
    with pytest.raises(HTTPBadRequest):
        validator(dict(a='abbcde'))


def test_validation_pattern():
    validator = RequestValidator(
        fields=dict(
            a=dict(pattern=r'^\D{5}$')
        )
    )

    assert dict(a='abcdJ') == validator(dict(a='abcdJ'))[0]

    # Param1 not matching
    with pytest.raises(HTTPBadRequest):
        validator(dict(a='asc'))


def test_validation_pattern_compiled():
    validator = RequestValidator(
        fields=dict(
            a=dict(pattern=re.compile(r'^\d{5}$'))
        )
    )

    assert dict(a='01234') == validator(dict(a='01234'))[0]

    # Param1 not matching
    with pytest.raises(HTTPBadRequest):
        validator(dict(a='123456'))


def test_validation_type():
    validator = RequestValidator(
        fields=dict(
            a=dict(type_=int),
            b=dict(type_=str),
            c=dict(type_=Decimal)
        )
    )

    assert dict(a=123, b='123', c=1.23) == \
        validator(dict(a='123', b=123, c=1.23))[0]

    # Param1 bad value(Cannot be converted to int)
    with pytest.raises(HTTPBadRequest):
        validator(dict(
            a='NotInteger',
        ))

    # Param3 bad value(Cannot be converted to decimal)
    with pytest.raises(HTTPBadRequest):
        validator(dict(c='NotDecimal'))


def test_validation_query_string():
    validator = RequestValidator(
        fields=dict(
            a=dict(query=True),
        )
    )

    # Accept query_string
    assert dict(a='value') == validator(query=dict(a='value'))[1]


def test_validation_custom_status():
    validator = RequestValidator(
        fields=dict(
            a=dict(
                type_=(int, '999 Type error'),
                minimum=(3, '666'),
                maximum=(4, '667 greater than maximum'),
            )
        )
    )

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a='NotInteger'))
    assert str(ctx.value) == '999 Type error'

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=2))
    assert str(ctx.value) == '666 Bad request'

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=5))
    assert str(ctx.value) == '667 greater than maximum'


def test_callable_validator():
    def f(age, container, field):
        age = int(age)
        if age < 0:
            raise ValueError('Age is not in valid range')
        return age

    validator = RequestValidator(
        fields=dict(
            a=f
        )
    )

    assert dict(a=12).items() == validator(dict(a=12))[0].items()

    with pytest.raises(ValueError):
        validator(dict(a=-1))


def test_not_none_validator():
    validator = RequestValidator(fields=dict(a=dict(not_none=True)))
    assert dict(a=1, b=2) == validator(dict(a=1, b=2))[0]
    assert dict(b=2) == validator(dict(b=2))[0]

    with pytest.raises(HTTPBadRequest):
        validator(dict(a=None))

    validator = RequestValidator(
        fields=dict(a=dict(not_none='666 a is null'))
    )
    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=None))
    assert '666 a is null' == str(ctx.value)

    with pytest.raises(TypeError):
        RequestValidator(fields=dict(a=dict(not_none=23)))


def test_readonly_validator():
    validator = RequestValidator(fields=dict(a=dict(readonly=True)))
    with pytest.raises(HTTPBadRequest):
        validator(dict(a=None))

    validator = RequestValidator(
        fields=dict(a=dict(not_none='666 a is readonly'))
    )
    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=None))
    assert '666 a is readonly' == str(ctx.value)

