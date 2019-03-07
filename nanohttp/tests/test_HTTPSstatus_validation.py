import re

import pytest
from bddrest import status, response

from nanohttp import RequestValidator, HTTPBadRequest, HTTPStatus, \
    Controller, validate


def test_not_null():
    class Myclass(HTTPStatus):
        status='666 a is readonly'

    validator = RequestValidator(fields=dict(a=dict(readonly=True)))
    with pytest.raises(HTTPBadRequest):
        validator(dict(a=None))

    validator = RequestValidator(
        fields=dict(a=dict(not_none=Myclass))
    )
    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=None))
    assert Myclass.status == str(ctx.value)

def test_validation_required_as_HTTPstatus():
    class Myclass(HTTPStatus):
        status='600 Custom exception'

    validator = RequestValidator(
        fields=dict(
            a=dict(required=Myclass)
        )
    )
    with pytest.raises(HTTPStatus(Myclass).__class__):
        validator(dict(another_param='value1'))

    assert dict(a='value1') == validator(dict(a='value1'))[0]

def test_httpstatus_as_validation_error():
    class MyStatusMin(HTTPStatus):
        status = '600 Greater than the minimum length'

    class MyStatusMax(HTTPStatus):
        status = '601 Greater than the maximum length'

    class MyStatusPattern(HTTPStatus):
        status = '602 Invalid input format'


    validator = RequestValidator(
        fields=dict(
            a=dict(
                min_length=(2, MyStatusMin),
                max_length=(5, MyStatusMax),
                pattern=(r'^[A-Z]*$', MyStatusPattern)
            )
        )
    )

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a='A'))
        assert str(ctx.value) == MyStatusMin.status

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a=(5 + 1) * 'A'))
    assert str(ctx.value) == MyStatusMax.status

    with pytest.raises(HTTPStatus) as ctx:
        validator(dict(a='abc'))
    assert str(ctx.value) == MyStatusPattern.status

