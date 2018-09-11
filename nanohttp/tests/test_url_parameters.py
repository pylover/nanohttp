from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_fixed_length_url_parameter():
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

