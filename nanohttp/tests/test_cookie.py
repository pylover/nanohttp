
import unittest
from http import cookies

from nanohttp import Controller, html, context
from nanohttp.tests.helpers import WsgiAppTestCase


class HttpCookieTestCase(WsgiAppTestCase):

    class Root(Controller):

        @html
        def index(self):
            if 'test-cookie' not in context.cookies:
                context.cookies['test-cookie'] = '0'

            counter = context.cookies['test-cookie']
            context.cookies['test-cookie'] = str(int(counter.value) + 1)
            context.cookies['test-cookie']['max-age'] = 1

            context.cookies['dummy-cookie'] = counter.value

            context.cookies['dummy-cookie3'] = counter.value
            context.cookies['dummy-cookie3']['domain'] = 'example.com'
            yield 'Index'

        @html
        def secure(self):
            context.cookies['dummy-cookie1'] = 'dummy'
            context.cookies['dummy-cookie1']['httponly'] = True

            context.cookies['dummy-cookie2'] = 'dummy'
            context.cookies['dummy-cookie2']['domain'] = 'example.com'

            context.cookies['dummy-cookie3'] = 'dummy'
            context.cookies['dummy-cookie3']['secure'] = True
            yield 'Secure'

        @html
        def clear(self):
            context.cookies['dummy-cookie'] = ''
            context.cookies['dummy-cookie']['expires'] = 'Sat, 01 Jan 2000 00:00:01 GMT'
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
    #
        response, content = self.assert_get('/clear')
        cookies_ = cookies.SimpleCookie(response['set-cookie'])
        self.assertIn('dummy-cookie', cookies_)
        self.assertEqual(cookies_['dummy-cookie']['expires'], 'Sat, 01 Jan 2000 00:00:01 GMT')
        self.assertEqual(cookies_['dummy-cookie'].value, '')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()