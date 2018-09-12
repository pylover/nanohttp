from bddrest import status, response

from nanohttp import Controller, action, HTTPStatus, settings, configure, json
from nanohttp.tests.helpers import Given, when


def test_http_status_debug_mode():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    with Given(Root()):
        assert status == '603 Bad Happened'
        assert 'traceback' in response.text.casefold()


def test_http_status_no_debug_mode():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    with Given(Root(), configuration='debug: false'):
        assert status == '603 Bad Happened'
        assert 'traceback' not in response.text.casefold()
        assert response.text == 'Bad Happened'


def test_http_status_debug_mode_json_content_type():
    class Root(Controller):
        @json
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    with Given(Root()):
        assert status == '603 Bad Happened'
        assert 'stackTrace' in response.json


def test_http_status_no_debug_mode_json_content_type():
    class Root(Controller):
        @json
        def index(self):
            raise HTTPStatus('603 Bad Happened')

    with Given(Root(), configuration='debug: false'):
        assert status == '603 Bad Happened'
        assert response.json == {}

