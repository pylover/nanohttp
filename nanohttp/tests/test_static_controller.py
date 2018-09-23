from bddrest import status, response

from nanohttp import Static, Controller
from nanohttp.tests.helpers import Given, when


def test_static_controller(make_temp_directory):
    static = Static(
        make_temp_directory(a=dict(a1='A1', a2='A2'), b='B'),
        default_document='b'
    )
    with Given(static):
        assert status == 200
        assert response.text == 'B'

        when('/a/a1')
        assert status == 200
        assert response.text == 'A1'

        when('/a/a2')
        assert status == 200
        assert response.text == 'A2'

        when('/a/a3')
        assert status == 404

        when('/../')
        assert status == 403

        when('/a/../a/a2')
        assert status == 200

        # When default document is not exists
        static.default_document = 'BadFile'
        when('/')
        assert status == 404

        # When default document is not given
        static.default_document = None
        when('/')
        assert status == 404


def test_nested_static_controller(make_temp_directory):
    class Root(Controller):
        static = Static(
            make_temp_directory(a=dict(a1='A1', a2='A2'), b='B'),
            default_document='b'
        )

    with Given(Root()):
        assert status == 404

        when('/static/b')
        assert status == 200
        assert response.text == 'B'

        when('/static/a/a1')
        assert status == 200
        assert response.text == 'A1'

