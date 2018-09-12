from bddrest import status, response

from nanohttp import Controller, action
from nanohttp.tests.helpers import Given, when


def test_action_decorator_verbs():
    class Root(Controller):
        @action(verbs=['get', 'view'])
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.text == '1, 2'

        when(verb='put')
        assert status  == 405


def test_action_decorator_content_type():
    class Root(Controller):
        @action(encoding='utf32', content_type='text/plain')
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.encoding == 'utf32'
        assert response.content_type == 'text/plain'
        assert response.text == '1, 2'


