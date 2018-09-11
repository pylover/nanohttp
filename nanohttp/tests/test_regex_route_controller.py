from bddrest import status, response

from nanohttp import RegexRouteController, action
from nanohttp.tests.helpers import Given, when


def test_regex_controller():
    class Root(RegexRouteController):
        def __init__(self):
            super().__init__((
                (r'/foos/(?P<id>\d+)/bars',
                self.bars),
            ))

        @action
        def bars(self, id: int):
            return f'{id}'

    with Given(Root(), '/foos/1/bars'):
        assert status == 200
        assert response.text == '1'

        when('/foos')
        assert status == 404

        when('/foos/bars')
        assert status == 404

        when('/foos/1/2/bars')
        assert status == 404

        when('/foos/a/bars')
        assert status == 404

