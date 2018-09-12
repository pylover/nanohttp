from bddrest import status, response

from nanohttp import Controller, action, context, chunked
from nanohttp.tests.helpers import Given, when


def test_chunked_streaming():
    class Root(Controller):
        @action
        @chunked
        def index(self):
            yield 'first'
            yield 'second'

        @action
        @chunked('trailer1', 'end')
        def trailer(self):
            yield 'first'
            yield 'second'

        @action
        @chunked
        def error(self):
            yield 'first'
            raise Exception('error in streaming')

    with Given(Root()):
        assert status == 200
        assert response.text == \
            '5\r\nfirst\r\n6\r\nsecond\r\n0\r\n\r\n'

        when('/trailer')
        assert status == 200
        assert response.text == \
            '5\r\nfirst\r\n6\r\nsecond\r\n0\r\ntrailer1: end\r\n\r\n'

        when('/error')
        assert status == 200
        assert response.text == \
            '5\r\nfirst\r\n18\r\nerror in streaming0\r\n\r\n'
