from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_fixed_length_positional_url_parameter():
    class Root(Controller):
        @action
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == '200 OK'
        assert response.text == '1, 2'

        # Extra trailing slash
        when('/1/2/')
        assert status == '200 OK'
        assert response.text == '1, 2'

        # Insufficient URL parameters
        when('/1')
        assert status == '404 Not Found'

        # Extra URL parameters
        when('/1/2/3')
        assert status  == '404 Not Found'


def test_vary_length_positional_url_parameters():
    class Root(Controller):
        @action
        def index(self, *args):
            yield ', '.join(args)

    with Given(Root()):
        assert status == '200 OK'
        assert response.text == ''

        when('/a')
        assert status == 200
        assert response.text == 'a'

        when('/a/b')
        assert status == 200
        assert response.text == 'a, b'


def test_fixed_length_keyword_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, a=None, b=1):
            yield f'{a}, {b}'

    with Given(Root()):
        assert status == '200 OK'
        assert response.text == 'None, 1'

        when('/a')
        assert status == '200 OK'
        assert response.text == 'a, 1'

        when('/a/b')
        assert status == 200
        assert response.text == 'a, b'

        when('/a/b/c')
        assert status == 404


def test_vary_length_keyword_arguments_url_parameters():
    class Root(Controller):
        @action
        def index(self, **kw):
            yield ', '.join(f'{k}={v}' for k, v in kw.items())

    from pudb import set_trace; set_trace()
    with Given(Root()):
        assert status == '200 OK'
        assert response.text == ''

        when('/a')
        assert status == 404
