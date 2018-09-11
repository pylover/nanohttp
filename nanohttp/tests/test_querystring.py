from bddrest import status, response

from nanohttp import Controller, action, context
from nanohttp.tests.helpers import Given, when


def test_query_strign():
    class Root(Controller):
        @action
        def index(self, *, a=1, b=2):
            query = ', '.join(f'{k}={v}' for k, v in context.query.items())
            yield f'{a}, {b}, {query}'

    with Given(Root()):
        assert status == 200
        assert response.text == '1, 2, '

        when(query=dict(a='a'))
        assert status == 200
        assert response.text == 'a, 2, a=a'

        when(query=dict(a='a', c='c'))
        assert status == 200
        assert response.text == 'a, 2, a=a, c=c'

        when(query=dict(c='c'))
        assert status == 200
        assert response.text == '1, 2, c=c'
