from bddrest import status, response

from nanohttp import Controller, action


def test_default_handler(given, when):
    class Root(Controller):
        @action
        def index(self):
            yield 'Index'

    with given(Root()):
        assert status == '200 OK'
        assert response.text == 'Index'

        when(url='/a')
        assert status == '404 Not Found'
