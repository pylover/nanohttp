import pytest
from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_basic_pipeline():
    class Root(Controller):
        @action
        def index(self):
            yield 'Index'

    with Given(Root()):
        assert status == 200
        assert response.text == 'Index'


def test_iterable_pipeline():
    class Root(Controller):
        @action
        def index(self):
            return ['a', 'b']

    with Given(Root()):
        assert status == 200
        assert response.text == 'ab'


def test_bad_response():
    class Root(Controller):
        @action
        def index(self):
            return 352345352

    with pytest.raises(ValueError):
        Given(Root())


def test_empty_response():
    class Root(Controller):
        @action
        def index(self):
            return None

    with Given(Root()):
        assert status == 200
        assert response.text == ''


