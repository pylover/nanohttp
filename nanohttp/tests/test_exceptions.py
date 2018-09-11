from bddrest import status, response

from nanohttp import Controller, action, HTTPStatus, settings, configure
from nanohttp.tests.helpers import Given, when


def test_http_status():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    with Given(Root()):
        assert status == '603 Bad Happened'

