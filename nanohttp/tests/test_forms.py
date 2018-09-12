import io
import cgi

from bddrest import status, response

from nanohttp import Controller, action, context
from nanohttp.tests.helpers import Given, when


def test_http_url_encoded_form():
    class Root(Controller):
        @action
        def index(self):
            yield context.request_content_type
            yield ', '
            yield ', '.join(
                f'{k}={v}' for k, v in sorted(context.form.items())
            )

    with Given(Root(), verb='POST'):
        assert status == 200
        assert response.text == ', '

        when(form=dict(a=1, b=2))
        assert status == 200
        assert response.text == 'application/x-www-form-urlencoded, a=1, b=2'

        when(body='a')
        assert status == 200
        assert response.text == ', a='


def test_http_multipart_form():
    class Root(Controller):
        @action
        def index(self):
            def read_form_field(v):
                return v.file.read().decode() \
                    if isinstance(v, cgi.FieldStorage) else v
            yield context.request_content_type
            yield ', '
            yield ', '.join(
                f'{k}='
                f'{read_form_field(v)}' \
                for k, v in sorted(context.form.items())
            )

    with Given(Root(), verb='POST'):
        assert status == 200
        assert response.text == ', '

        when(multipart=dict(a=1, b=2))
        assert status == 200
        assert response.text == 'multipart/form-data, a=1, b=2'

        filelike = io.BytesIO(b'abcdef')
        when(multipart=dict(a=filelike))
        assert status == 200
        assert response.text == 'multipart/form-data, a=abcdef'


def test_json_form():
    class Root(Controller):
        @action
        def index(self):
            yield context.request_content_type
            yield ', '
            yield ', '.join(
                f'{k}={v}' for k, v in sorted(context.form.items())
            )

    with Given(Root(), verb='POST', json={}):
        assert status == 200
        assert response.text == ', '

        when(json=dict(a=1, b=2))
        assert status == 200
        assert response.text == 'application/json, a=1, b=2'

