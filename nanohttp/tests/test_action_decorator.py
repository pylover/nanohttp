import pytest
from bddrest import status, response, given

from nanohttp import Controller, action, html, json, text, xml, binary
from nanohttp.tests.helpers import Given, when


def test_action_decorator_verbs():
    class Root(Controller):
        @action(verbs=['get', 'view'])
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.text == '1, 2'

        when(verb='put')
        assert status  == 405


def test_action_decorator_content_type():
    class Root(Controller):
        @action(encoding='utf32', content_type='text/plain')
        def index(self, a, b):
            yield f'{a}, {b}'

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.encoding == 'utf32'
        assert response.content_type == 'text/plain'
        assert response.text == '1, 2'


def test_action_decorator_prevent_form():
    class Root(Controller):
        @action(prevent_form=True)
        def index(self):
            yield 'default'

        @action(prevent_form='777 Form Not Allowedi Here')
        def custom_status(self):
            yield 'custom'

    with Given(Root(), verb='POST'):
        assert status == 200

        when(form=dict(a=1))
        assert status == 400

        when('/custom_status', form=dict(a=1))
        assert status == 777

        when('/custom_status')
        assert status == 200


def test_action_decorator_prevent_empty_form():
    class Root(Controller):
        @action(prevent_empty_form=True)
        def index(self):
            yield 'default'

        @action(prevent_empty_form='777 Form Is Required Here')
        def custom_status(self):
            yield 'custom'

    with Given(Root(), verb='POST', form=dict(a=1)):
        assert status == 200

        when(form={})
        assert status == 400

        when(form=None)
        assert status == 400

        when('/custom_status', form={})
        assert status == 777

        when('/custom_status', form=None)
        assert status == 777

        when('/custom_status', form=dict(a=1))
        assert status == 200


def test_action_decorator_form_whitelist():
    class Root(Controller):
        @action(form_whitelist=['a', 'b'])
        def index(self):
            yield 'default'

        @action(form_whitelist=(['a', 'b'], '888 Only a & b accepted'))
        def custom_status(self):
            yield 'custom'

    with Given(Root(), verb='POST', form=dict(a=1)):
        assert status == 200

        when(form=given + dict(b=2))
        assert status == 200

        when(form=given + dict(c=2))
        assert status == 400

        when('/custom_status', form=dict(c=2))
        assert status == 888

        when('/custom_status', form=dict(a=2))
        assert status == 200


def test_html_decorator():
    class Root(Controller):
        @html
        def index(self):
            yield '<html></html>'

    with Given(Root()):
        assert status == 200
        assert response.text == '<html></html>'
        assert response.content_type == 'text/html'
        assert response.encoding == 'utf-8'


def test_json_decorator():
    class Root(Controller):
        @json
        def index(self, a, b):
            return dict(a=a, b=b)

        @json
        def custom(self):
            class A:
                def to_dict(self):
                    return dict(c=1)
            return A()

        @json
        def badobject(self):
            class A:
                pass
            return A()

    with Given(Root(), '/1/2'):
        assert status == 200
        assert response.json == dict(a='1', b='2')
        assert response.content_type == 'application/json'
        assert response.encoding == 'utf-8'

        when('/custom')
        assert status == 200
        assert response.json == dict(c=1)

        with pytest.raises(ValueError):
            when('/badobject')


def test_text_decorator():
    class Root(Controller):
        @text
        def index(self):
            yield 'abc'

    with Given(Root()):
        assert status == 200
        assert response.text == 'abc'
        assert response.content_type == 'text/plain'
        assert response.encoding == 'utf-8'


def test_xml_decorator():
    class Root(Controller):
        @xml
        def index(self):
            yield '<xml></xml>'

    with Given(Root()):
        assert status == 200
        assert response.text == '<xml></xml>'
        assert response.content_type == 'application/xml'
        assert response.encoding == 'utf-8'


def test_binary_decorator():
    class Root(Controller):
        @binary
        def index(self):
            yield b'abc'

    with Given(Root()):
        assert status == 200
        assert response.body == b'abc'
        assert response.content_type == 'application/octet'
        assert response.encoding is None

