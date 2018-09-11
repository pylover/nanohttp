from bddrest import status, response

from nanohttp import Controller, action, HTTPStatus, settings, configure


def test_http_status(given, when):
    class Root(Controller):
        @action
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    configure()
    with given(Root()):
        assert status == '603 Bad Happened'

