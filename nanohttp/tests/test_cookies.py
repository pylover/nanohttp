from http import cookies


import pytest
from bddrest import status, response

from nanohttp import Controller, action, context
from nanohttp.tests.helpers import Given, when


def test_basic_pipeline():
    class Root(Controller):
        @action
        def index(self):
            counter = context.cookies['counter']
            context.cookies['counter'] = str(int(counter.value) + 1)
            context.cookies['counter']['max-age'] = 1
            context.cookies['counter']['path'] = '/a'
            context.cookies['counter']['domain'] = 'example.com'
            yield 'Index'

    headers = {'Cookie': 'counter=1;'}
    with Given(Root(), headers=headers):
        assert status == 200
        assert response.text == 'Index'
        assert 'Set-cookie' in response.headers
        cookie = cookies.SimpleCookie(response.headers['Set-cookie'])
        counter = cookie['counter']
        assert counter.value == '2'
        assert counter['path'] == '/a'
        assert counter['domain'] == 'example.com'
        assert counter['max-age'] == '1'

