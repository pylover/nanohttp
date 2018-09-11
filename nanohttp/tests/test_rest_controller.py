from bddrest import status, response

from nanohttp import RestController, action
from nanohttp.tests.helpers import Given, when


def test_rest_controller():
    class Root(RestController):

        @action
        def index(self):  # pragma: no cover
            raise Exception()

        @action
        def foo(self, *args):
            yield f'Foo, {", ".join(args)}'

        def private(self):  # pragma: no cover
            raise Exception()

    with Given(Root(), verb='foo'):
        assert status == 200
        assert response.text == 'Foo, '

        when(verb='FOO')
        assert status == 200
        assert response.text == 'Foo, '

        when('/a', verb='FOO')
        assert status == 200
        assert response.text == 'Foo, a'

        when('/a/b', verb='FOO')
        assert status == 200
        assert response.text == 'Foo, a, b'

        when(verb='GET')
        assert status == 405

        when('/private')
        assert status == 404

        when('/private', verb='GET')
        assert status == 404


def test_nested_rest_controllers():
    class BarController(RestController):
        @action
        def get(self, *args):
            yield f'Bars, {", ".join(args)}'

    class Root(RestController):
        bars = BarController()

        @action
        def get(self, *args):
            yield f'{", ".join(args)}'

    with Given(Root()):
        assert status == 200
        assert response.text == ''

        when('/bars')
        assert status == 200
        assert response.text == 'Bars, '

        when('/bars/a')
        assert status == 200
        assert response.text == 'Bars, a'

