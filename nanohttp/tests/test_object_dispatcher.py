from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_object_dispatcher():
    class RegularClass:
        pass

    class BarController(Controller):
        @action
        def index(self, *args):
            yield f'Bars, {", ".join(args)}'

        def private(self):  # pragma: no cover
            raise Exception()

        @action
        def lorem(self, *args):
            yield f'Lorem, {", ".join(args)}'

    class Root(Controller):
        bars = BarController()
        requlars = RegularClass()

        @action
        def index(self):
            yield 'Index'

        @action
        def foo(self):
            yield 'Foo'

        def private(self):  # pragma: no cover
            raise Exception()

    with Given(Root()):
        assert status == 200
        assert response.text == 'Index'

        when('/foo')
        assert status == 200
        assert response.text == 'Foo'

        when(url='/a')
        assert status == '404 Not Found'

        when(url='/a/')
        assert status == '404 Not Found'

        when(url='/requlars')
        assert status == '404 Not Found'

        when('/private')
        assert status == 404

        when('/bars')
        assert status == 200
        assert response.text == 'Bars, '

        when('/bars/a')
        assert status == 200
        assert response.text == 'Bars, a'

        when('/bars/lorem')
        assert status == 200
        assert response.text == 'Lorem, '

        when('/bars/lorem/a/b')
        assert status == 200
        assert response.text == 'Lorem, a, b'

        when('/bars/private')
        assert status == 404

