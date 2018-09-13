import pytest
from bddrest import status, response

from nanohttp import Controller, action, context
from nanohttp.tests.helpers import Given, when


def test_basic_pipeline():
    class Root(Controller):
        @action
        def index(self):
            yield f'Index: {context.request_scheme}, {context.request_uri}'

    with Given(Root()):
        assert status == 200
        assert response.text == 'Index: http, http://bddrest-interceptor/'


def test_no_default_handler():
    class Root(Controller):
        @action
        def foo(self):
            yield 'Foo'

    with Given(Root(), '/foo'):
        assert status == 200
        assert response.text == 'Foo'

        when('/')
        assert status == 404


def test_iterable_pipeline():
    class Root(Controller):
        @action
        def index(self):
            return ['a', 'b']

    with Given(Root()):
        assert status == 200
        assert response.text == 'ab'


def test_not_iterable_response():
    class Root(Controller):
        @action
        def index(self):
            return 352345352

    with pytest.raises(ValueError):
        Given(Root())


def test_iterable_but_bad_response():
    class Root(Controller):
        @action
        def index(self):
            yield '1'
            yield 352345352

    with pytest.raises(TypeError):
        Given(Root())


def test_empty_response():
    class Root(Controller):
        @action
        def index(self):
            return None

    with Given(Root()):
        assert status == 200
        assert response.text == ''

