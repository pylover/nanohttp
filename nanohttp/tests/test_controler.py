from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_controller():
    class Root(Controller):
        __translation__ = dict(bar='foo')

        @action
        def foo(self):
            yield 'Bar'


    with Given(Root(), '/foo', 'bar'):
        assert status == 200
        assert response.text == 'Bar'

