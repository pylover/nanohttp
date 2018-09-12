from bddrest import status, response, given

from nanohttp import Controller, json
from nanohttp.tests.helpers import Given, when


def test_json_decorator():
    class Root(Controller):
        @json
        def index(self, a, b):
            return dict(a=a, b=b)

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.json == dict(a='1', b='2')
        assert response.content_type == 'application/json'
        assert response.encoding == 'utf-8'



