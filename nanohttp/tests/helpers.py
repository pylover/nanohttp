import sys
import unittest
import base64
import mimetypes
import socket
import io
from hashlib import md5
from os import path, urandom
from urllib.parse import urlencode

import httplib2
from wsgi_intercept import WSGIAppError
from wsgi_intercept.interceptor import Httplib2Interceptor

from nanohttp import Controller, configure, Application

TEST_DIR = path.abspath(path.dirname(__file__))
STUFF_DIR = path.join(TEST_DIR, 'stuff')


def md5sum(f):
    if isinstance(f, str):
        file_obj = open(f, 'rb')
    else:
        file_obj = f

    try:
        checksum = md5()
        while True:
            d = file_obj.read(0x8000)
            if not d:
                break
            checksum.update(d)
        return checksum.digest()
    finally:
        if file_obj is not f:
            file_obj.close()


class WsgiTester(httplib2.Http):

    def __init__(self, app_factory, host='nanohttp.org', port=80, **kw):
        super(WsgiTester, self).__init__()
        self.force_exception_to_status_code
        self.interceptor = Httplib2Interceptor(app_factory, host=host, port=port, **kw)

    def __enter__(self):
        self.interceptor.__enter__()
        return self

    def __exit__(self, exc_type, value, traceback):
        self.interceptor.__exit__(exc_type, value, traceback)

    def request(self, uri, query_string=None, fields=None, files=None, json=None, **kw):
        headers = kw.setdefault('headers', {})
        body = None

        if files:
            content_type, body, length = encode_multipart_data(fields, files)
            body = body.getvalue()
            headers.setdefault('Content-Type', content_type)
        elif fields:
            body = urlencode(fields)
            headers.setdefault('Content-Type', 'application/x-www-form-urlencoded')
        elif json:
            body = json
            headers.setdefault('Content-Type', 'application/json')

        if query_string:
            uri += '%s%s' % ('&' if '?' in uri else '?', urlencode(query_string))

        try:
            return super(WsgiTester, self).request(
                '%s%s' % (self.interceptor.url, uri),
                body=body,
                **kw
            )
        except WSGIAppError as e:
            content = b"Internal server error."
            response = httplib2.Response({
                "content-type": "text/plain",
                "status": "408",
                "content-length": len(content)
            })
            response.reason = content
            response.status = 500
            return response, content


class WsgiAppTestCase(unittest.TestCase):

    class Root(Controller):
        pass

    class Application(Application):
        pass

    def setUp(self):
        configure(force=True)
        self.application = self.Application(self.Root())
        self.client = WsgiTester(lambda: self.application)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(*sys.exc_info())

    def assert_request(self, uri, method, cookies=None, expected_response=None, expected_checksum=None,
                       not_expected_headers=None, expected_headers=None, status=200, **kw):

        if cookies:
            headers = kw.setdefault('headers', {})
            if isinstance(cookies, str):
                headers['Cookie'] = cookies
            else:
                headers['Cookie'] = '; '.join('%s=%s' % (k, v.value) for k, v in cookies.items())

        response, content = self.client.request(uri, method=method, **kw)

        # if response.status == 500:
        #     print(content.decode(), file=sys.stderr)
        self.assertEqual(response.status, status)

        if expected_response is not None:
            if isinstance(expected_response, str):
                self.assertEqual(expected_response, content.decode())
            else:
                self.assertRegex(content.decode(), expected_response)

        for k, v in (expected_headers or {}).items():
            k = k.lower()
            if isinstance(v, str):
                self.assertEqual(response[k], v)
            else:
                self.assertRegex(response[k], v)

        for k in not_expected_headers or []:
            self.assertNotIn(k.lower(), response)

        if expected_checksum:
            self.assertEqual(md5sum(io.BytesIO(content)), expected_checksum)

        return response, content

    def assert_get(self, uri, *args, **kw):
        return self.assert_request(uri, 'get', *args, **kw)

    def assert_options(self, uri, *args, **kw):
        return self.assert_request(uri, 'options', *args, **kw)

    def assert_post(self, uri, *args, **kw):
        return self.assert_request(uri, 'post', *args, **kw)

    def assert_put(self, uri, *args, **kw):
        return self.assert_request(uri, 'put', *args, **kw)

    def assert_delete(self, uri, *args, **kw):
        return self.assert_request(uri, 'delete', *args, **kw)


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


def find_free_tcp_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket.gethostname(), 0))
        return s.getsockname()[1]
    finally:
        s.close()


if __name__ == '__main__':  # pragma: no cover
    ct, b, len_ = encode_multipart_data(dict(test1='TEST1VALUE'), files=dict(cat='stuff/cat.jpg'))
    print(ct)
    print(len_)
    print(b.read())
