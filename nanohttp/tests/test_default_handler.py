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

        when(verb='PUT')
        assert status == '405 Method Not Allowed'


def test_default_handler_with_positional_arguments():
    class Root(Controller):
        @action
        def index(self, arg1):
            yield f'{arg1}'

    with Given(Root(), '/a'):
        assert status == 200
        assert response.text == 'a'

        when(url='/')
        assert status == 404


def test_default_handler_with_vary_positional_arguments():
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


def test_default_handler_with_keyword_arguments():
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

