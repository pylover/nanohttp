import re
from decimal import Decimal

import pytest
from bddrest import status, response

from nanohttp import RequestValidator, HTTPBadRequest, HTTPStatus, \
    Controller, validate, action, context
from nanohttp.tests.helpers import Given


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


