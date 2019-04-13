import pytest
from bddrest import status, response

from nanohttp import Controller, action, json, context, HTTPStatus, \
    HTTPBadRequest, HTTPMovedPermanently, HTTPNotModified, HTTPNoContent, \
    HTTPCreated, HTTPAccepted, HTTPNonAuthoritativeInformation, \
    HTTPResetContent, HTTPPartialContent
from nanohttp.tests.helpers import Given


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


def test_http_bad_request():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPBadRequest('My Bad')

    with Given(Root(), configuration='debug: false'):
        assert status == '400 My Bad'
        assert response.text == 'My Bad'


def test_http_not_modified():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPNotModified()

    with Given(Root()):
        assert status == 304


def test_http_redirect():
    class Root(Controller):
        @action
        def index(self):
            raise HTTPMovedPermanently('http://example.com')

    with Given(Root(), configuration='debug: false'):
        assert status == '301 Moved Permanently'
        assert response.text == 'Moved Permanently'
        assert response.headers['Location'] == 'http://example.com'


def test_unhandled_exceptions_debug_mode():
    class E(Exception):
        pass

    class Root(Controller):
        @action
        def index(self):
            raise E()

    with pytest.raises(E):
        Given(Root())


def test_unhandled_exceptions_no_debug_mode():
    class E(Exception):
        pass

    class Root(Controller):
        @action
        def index(self):
            raise E()

    with pytest.raises(E):
        Given(Root(), configuration='debug: false')


@pytest.mark.parametrize(
    'http_success_exception',
    (
        HTTPNoContent,
        HTTPCreated,
        HTTPAccepted,
        HTTPNonAuthoritativeInformation,
        HTTPResetContent,
        HTTPPartialContent,
    )
)
def test_http_success_headers(http_success_exception):
    class Root(Controller):
        @action
        def index(self):
            context.response_headers['x-app-extra'] = 'yep'
            raise http_success_exception

    with Given(Root()):
        assert status == http_success_exception.status
        assert response.headers['x-app-extra'] == 'yep'

