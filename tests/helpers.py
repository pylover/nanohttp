import sys
import unittest
import base64
import mimetypes
import io
from os import path, urandom
from urllib.parse import urlencode

import httplib2
from wsgi_intercept.interceptor import Httplib2Interceptor

from nanohttp import Controller

TEST_DIR = path.abspath(path.dirname(__file__))
STUFF_DIR = path.join(TEST_DIR, 'stuff')


class WsgiTester(httplib2.Http):

    def __init__(self, app_factory, host='nanohttp.org', port=80, **kw):
        super(WsgiTester, self).__init__()
        self.interceptor = Httplib2Interceptor(app_factory, host=host, port=port, **kw)

    def __enter__(self):
        self.interceptor.__enter__()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.interceptor.__exit__(exc_type, value, traceback)

    def request(self, uri, query_string=None, fields=None, files=None, **kw):
        headers = {}
        body = None

        if files:
            content_type, body, length = encode_multipart_data(fields, files)
            body = body.getvalue()
            headers['Content-Type'] = content_type
        elif fields:
            body = urlencode(fields)
            headers['Content-Type'] = 'application/x-www-form-urlencoded'

        if query_string:
            uri += '%s%s' % ('&' if '?' in uri else '?', urlencode(query_string))

        return super(WsgiTester, self).request(
            '%s%s' % (self.interceptor.url, uri),
            body=body,
            headers=headers,
            **kw
        )


class WsgiAppTestCase(unittest.TestCase):

    class Root(Controller):
        pass

    def setUp(self):
        self.client = WsgiTester(self.Root().load_app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(*sys.exc_info())

    def assert_request(self, uri, method, resp=None, status=200, content_type=None, **kw):
        response, content = self.client.request(uri, method=method, **kw)
        self.assertEqual(response.status, status)

        if resp is not None:
            if isinstance(resp, str):
                self.assertEqual(content.decode(), resp)
            else:
                self.assertRegex(content.decode(), resp)

        if content_type:
            self.assertEqual(response['content-type'], content_type)

        return response, content

    def assert_get(self, uri, *args, **kw):
        return self.assert_request(uri, 'get', *args, **kw)

    def assert_post(self, uri, *args, **kw):
        return self.assert_request(uri, 'post', *args, **kw)


def encode_multipart_data(fields=None, files=None):  # pragma: no cover
    boundary = ''.join(['-----', base64.urlsafe_b64encode(urandom(27)).decode()])
    crlf = b'\r\n'
    lines = []

    if fields:
        for key, value in fields.items():
            lines.append('--' + boundary)
            lines.append('Content-Disposition: form-data; name="%s"' % key)
            lines.append('')
            lines.append(value if isinstance(value, str) else str(value))

    if files:
        for key, file_path in files.items():
            filename = path.split(file_path)[1]
            lines.append('--' + boundary)
            lines.append(
                'Content-Disposition: form-data; name="%s"; filename="%s"' %
                (key, filename))
            lines.append(
                'Content-Type: %s' %
                (mimetypes.guess_type(filename)[0] or 'application/octet-stream'))
            lines.append('')
            with open(file_path, 'rb') as f:
                lines.append(f.read())

    lines.append('--' + boundary + '--')
    lines.append('')

    body = io.BytesIO()
    length = 0
    for l in lines:
        # noinspection PyTypeChecker
        line = (l if isinstance(l, bytes) else l.encode()) + crlf
        length += len(line)
        body.write(line)
    body.seek(0)
    content_type = 'multipart/form-data; boundary=%s' % boundary
    return content_type, body, length


if __name__ == '__main__':  # pragma: no cover
    ct, b, len_ = encode_multipart_data(dict(test1='TEST1VALUE'), files=dict(cat='stuff/cat.jpg'))
    print(ct)
    print(len_)
    print(b.read())
