from bddrest import status, response, given

from nanohttp import Controller, action
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

