
from http import cookies

from nanohttp import Controller, html, context, HTTPCookie
from tests.helpers import WsgiAppTestCase


class HttpCookieTestCase(WsgiAppTestCase):

    class Root(Controller):

        @html
        def index(self):
            counter = int(context.cookies.get('test-cookie', 0))
            counter += 1
            context.response_cookies.append(HTTPCookie('test-cookie', value=str(counter), max_age=1))
            context.response_cookies.append(HTTPCookie('dummy-cookie', value=str(counter)))
            context.response_cookies.append(HTTPCookie('dummy-cookie3', value=str(counter), domain='example.com'))
            return 'Index'

        @html
        def secure(self):
            context.response_cookies.append(HTTPCookie('dummy-cookie1', value='dummy', http_only=True))
            context.response_cookies.append(HTTPCookie('dummy-cookie2', value='dummy', domain='example.com'))
            context.response_cookies.append(HTTPCookie('dummy-cookie3', value='dummy', secure=True))
            return 'Index'


    def test_cookie(self):

        response, content = self.assert_get('/')
        cookies_ = cookies.SimpleCookie(response['set-cookie'])
        self.assertEqual(cookies_['test-cookie'].value, '1')
        self.assertIn('dummy-cookie', cookies_)

        response, content = self.assert_get('/', cookies=cookies_)
        cookies_ = cookies.SimpleCookie(response['set-cookie'])
        self.assertEqual(cookies_['test-cookie'].value, '2')
        self.assertIn('dummy-cookie', cookies_)

        response, content = self.assert_get('/secure')
        cookies_ = cookies.SimpleCookie(response['set-cookie'])
        self.assertNotIn('dummy-cookie1', cookies_)
        self.assertNotIn('dummy-cookie2', cookies_)
        self.assertNotIn('dummy-cookie3', cookies_)
