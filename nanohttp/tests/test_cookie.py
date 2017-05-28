
import unittest
from http import cookies

from nanohttp import Controller, html, context, HttpCookie
from nanohttp.tests.helpers import WsgiAppTestCase


class HttpCookieTestCase(WsgiAppTestCase):

    class Root(Controller):

        @html
        def index(self):
            counter = int(context.cookies.get('test-cookie', 0))
            counter += 1
            context.response_cookies.append(HttpCookie('test-cookie', value=str(counter), max_age=1))
            context.response_cookies.append(HttpCookie('dummy-cookie', value=str(counter)))
            context.response_cookies.append(HttpCookie('dummy-cookie3', value=str(counter), domain='example.com'))
            yield 'Index'

        @html
        def secure(self):
            context.response_cookies.append(HttpCookie('dummy-cookie1', value='dummy', http_only=True))
            context.response_cookies.append(HttpCookie('dummy-cookie2', value='dummy', domain='example.com'))
            context.response_cookies.append(HttpCookie('dummy-cookie3', value='dummy', secure=True))
            yield 'Secure'

        @html
        def clear(self):
            context.response_cookies.append(HttpCookie.delete('dummy-cookie'))
            yield 'remove'

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

        response, content = self.assert_get('/clear')
        cookies_ = cookies.SimpleCookie(response['set-cookie'])
        self.assertIn('dummy-cookie', cookies_)
        self.assertEqual(cookies_['dummy-cookie']['expires'], 'Sat, 01 Jan 2000 00:00:01 GMT')

    def test_cookie_errors(self):
        self.assert_get('/', cookies='Invalid; token; data', status=400)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()