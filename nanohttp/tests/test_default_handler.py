from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_default_handler():
    class Root(Controller):
        @action(verbs=['get', 'post'])
        def index(self):
            yield 'Index'

    with Given(Root()):
        assert status == '200 OK'
        assert response.text == 'Index'

        when(url='/a')
        assert status == '404 Not Found'

        # TODO: move it to test action decorator
        when(verb='PUT')
        assert status == '405 Method Not Allowed'


