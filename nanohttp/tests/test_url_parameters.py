from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_fixed_positional_url_parameter():
    class Root(Controller):
        @action
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.text == '1, 2'

        # Extra trailing slash
        when('/1/2/')
        assert status == 200
        assert response.text == '1, 2'

        # Insufficient URL parameters
        when('/1')
        assert status == 404

        # Extra URL parameters
        when('/1/2/3')
        assert status  == 404


def test_vary_positional_url_parameters():
    class Root(Controller):
        @action
        def index(self, *args):
            yield ', '.join(args)

    with Given(Root()):
        assert status == 200
        assert response.text == ''

        when('/a')
        assert status == 200
        assert response.text == 'a'

        when('/a/b')
        assert status == 200
        assert response.text == 'a, b'


def test_fixed_optional_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, a=None, b=1):
            yield f'{a}, {b}'

    with Given(Root()):
        assert status == 200
        assert response.text == 'None, 1'

        when('/a')
        assert status == 200
        assert response.text == 'a, 1'

        when('/a/b')
        assert status == 200
        assert response.text == 'a, b'

        when('/a/b/c')
        assert status == 404


def test_vary_optional_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, **kw):
            yield ', '.join(f'{k}={v}' for k, v in kw.items())

    with Given(Root()):
        assert status == 200
        assert response.text == ''

        when('/a')
        assert status == 404


def test_both_vary_optional_and_positional_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, *a, **kw):
            yield ', '.join(a)

    with Given(Root()):
        assert status == 200
        assert response.text == ''

        when('/a')
        assert status == 200
        assert response.text == 'a'

        when('/a/b/c/d')
        assert status == 200
        assert response.text == 'a, b, c, d'


def test_fixed_positional_and_vary_optional_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, a, b, **kw):
            yield f'{a}, {b}, {kw}'

    with Given(Root(), '/a/b'):
        assert status == 200
        assert response.text == 'a, b, {}'

        when('/a')
        assert status == 404

        when('/a/b/c')
        assert status == 404


def test_both_fixed_positional_and_optional_arguments():
    class Root(Controller):
        @action
        def index(self, a, b, c=None):
            yield f'{a}, {b}, {c}'

    with Given(Root(), '/a/b'):
        assert status == 200
        assert response.text == 'a, b, None'

        when('/a/b/c')
        assert status == 200
        assert response.text == 'a, b, c'

        when('/a')
        assert status == 404

        when('/a/b/c/d')
        assert status == 404


def test_fixed_positional_and_both_vary_and_fixed_optional_arguments():
    class Root(Controller):
        @action
        def index(self, a, b, c=None, **kw):
            yield f'{a}, {b}, {c}, {kw}'

    with Given(Root(), '/a/b'):
        assert status == 200
        assert response.text == 'a, b, None, {}'

        when('/a/b/c')
        assert status == 200
        assert response.text == 'a, b, c, {}'

        when('/a')
        assert status == 404

        when('/a/b/c/d')
        assert status == 404


def test_both_foxed_and_vary_positional_arguments():
    class Root(Controller):
        @action
        def index(self, a, b, *args):
            yield f'{a}, {b}, {", ".join(args)}'

    with Given(Root(), '/a/b'):
        assert status == 200
        assert response.text == 'a, b, '

        when('/a/b/c')
        assert status == 200
        assert response.text == 'a, b, c'

        when('/a')
        assert status == 404

        when('/a/b/c/d')
        assert status == 200


