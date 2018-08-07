import re
import ujson
import unittest
from os.path import join

from nanohttp import Controller, text, context
from nanohttp.tests.helpers import WsgiAppTestCase, STUFF_DIR


class FormTestCase(WsgiAppTestCase):
    class Root(Controller):

        @text('post')
        def index(self):
            if not context.form:
                yield 'empty'
            yield ', '.join('%s: %s' % (k, v)
                for k, v in sorted(context.form.items(), key=lambda x: x[0]))

        @text(prevent_empty_form='444 Empty Form')
        def noempty(self):
            yield ''


        @text(prevent_form='443 Request Payload Not Allowed')
        def noform(self):
            yield ''


    def test_simple_query_string(self):
        self.assert_post('/?a=1&b=&c=2', expected_response='a: 1, b: , c: 2')
        self.assert_post(
            '/?a=1&b=2&b=3',
            expected_response='a: 1, b: [\'2\', \'3\']'
        )

    def test_url_encoded(self):
        self.assert_post(
            '/',
            fields={
                'a': 1,
                'b': [2, 3],
            },
            expected_response='a: 1, b: [2, 3]'
        )

    def test_multipart(self):
        self.assert_post(
            '/',
            fields={
                'a': 1,
                'b': [2, 3],
            },
            files={'c': join(STUFF_DIR, 'cat.jpg')},
            expected_response=\
                re.compile(
                    'a: 1, b: \[2, 3\], c: FieldStorage\(\'c\', \'cat\.jpg.*'
                ),
        )

    def test_empty_form(self):
        self.assert_post(
            '/',
            fields={},
            expected_response='empty',
        )

        self.assert_post(
            '/noempty',
            status=444,
        )


        self.assert_post(
            '/noempty',
            fields={},
            status=444,
        )

        self.assert_post(
            '/noempty',
            fields={'a': 'a'},
        )


    def test_json(self):
        self.assert_post(
            '/',
            json=ujson.dumps({
                'a': 1,
                'b': [2, 3],
            }),
            expected_response='a: 1, b: [2, 3]',
        )
        self.assert_post(
            '/',
            json='{',
            status=400
        )

    def test_invalid_form(self):
        self.assert_post(
            '/',
            fields={
                'a': 1,
                'b': [2, 3],
            },
            status=400,
            headers={'Content-Type': 'invalid/content-type'}
        )

    def test_prevent_form(self):
        self.assert_post(
            '/noform',
        )

        self.assert_post(
            '/noform',
            fields={},
        )

        self.assert_post(
            '/noform',
            fields={'a': 'a'},
            status=443
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
