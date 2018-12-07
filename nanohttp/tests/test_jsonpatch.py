import pytest
import ujson

from nanohttp import context, json, text, RestController
from nanohttp.contexts import Context
from nanohttp.jsonpatch import JsonPatchControllerMixin


class BiscuitsController(RestController):
    @json
    def put(self, id_: int = None):
        result = {}
        result.update(context.form)
        result['id'] = id_
        result['a'] = context.query.get('a')
        return result

    @json
    def get(self, id_: int = None):
        result = {}
        result.update(context.form)
        result['id'] = id_
        return result

    @json
    def error(self):
        raise Exception()


class SimpleJsonPatchController(JsonPatchControllerMixin, RestController):
    biscuits = BiscuitsController()

    @text
    def get(self):
        yield 'hey'


def test_jsonpatch_rfc6902():
    environ = {
        'REQUEST_METHOD': 'PATCH'
    }
    with Context(environ):
        controller = SimpleJsonPatchController()
        context.form = [
            {
                'op': 'get',
                'path': '/'
            },
            {
                'op': 'put',
                'path': 'biscuits/1',
                'value': {'name': 'Ginger Nut'}
            },
            {
                'op': 'get',
                'path': 'biscuits/2',
                'value': {'name': 'Ginger Nut'}
            }
        ]
        result = ujson.loads(controller())
        assert len(result) == 3


def test_jsonpatch_error():
    environ = {
        'REQUEST_METHOD': 'PATCH'
    }
    with Context(environ), pytest.raises(Exception):
        controller = SimpleJsonPatchController()
        context.form = [
            {
                'op': 'put',
                'path': 'biscuits/1',
                'value': {'name': 'Ginger Nut'}
            },
            {
                'op': 'error',
                'path': 'biscuits',
                'value': None
            }
        ]

        controller()


def test_jsonpatch_querystring():
    environ = {
        'REQUEST_METHOD': 'PATCH',
        'QUERY_STRING': 'a=10'
    }
    with Context(environ):
        controller = SimpleJsonPatchController()
        context.form = [
            {
                'op': 'get',
                'path': '/'
            },
            {
                'op': 'put',
                'path': 'biscuits/1?a=1',
                'value': {'name': 'Ginger Nut'}
            },
            {
                'op': 'get',
                'path': 'biscuits/2',
                'value': {'name': 'Ginger Nut'}
            }
        ]
        result = ujson.loads(controller())
        assert len(result) == 3
        assert result[1]['a'] == '1'
        assert 'a' not in result[0]
        assert 'a' not in result[2]


def test_jsonpatch_caseinsesitive_verb():
    environ = {
        'REQUEST_METHOD': 'PATCH',
        'QUERY_STRING': 'a=10'
    }
    with Context(environ):
        controller = SimpleJsonPatchController()
        context.form = [
            {'op': 'GET', 'path': '/'},
            {'op': 'PUT', 'path': 'biscuits/1?a=1', 'value': {
                'name':
                'Ginger Nut'
            }},
            {'op': 'GET', 'path': 'biscuits/2', 'value': {
                'name': 'Ginger Nut'
            }},
        ]
        result = ujson.loads(controller())
        assert len(result) == 3

