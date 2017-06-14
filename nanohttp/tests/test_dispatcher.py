
import unittest

from nanohttp import Controller, html, json, RestController, text
from nanohttp.tests.helpers import WsgiAppTestCase


class LinksController(Controller):

    @html
    def index(self, article_id: int=None, link_id: int=None):
        if link_id:
            yield 'Article: %s, Links index: %s' % (article_id, link_id)
        else:
            yield 'Link1, Link2, Link3'


class ArticleController(RestController):
    __detect_verb_by_header__ = 'HTTP_X_HTTP_VERB'
    links = LinksController()

    @html
    def get(self, article_id: int=None):
        yield "GET Article%s" % (
            's' if not article_id else (': ' + article_id)
        )

    @html
    def post(self):
        yield "POST Article"

    @html
    def put(self, article_id: int=None, inner_resource: str=None, link_id: int=None):
        if inner_resource == 'links':
            yield from self.links(article_id, link_id)
        else:
            yield "PUT Article: %s" % article_id

    def disallowed(self):  # pragma: no cover
        yield 'bad'


class DispatcherTestCase(WsgiAppTestCase):

    class Root(Controller):

        articles = ArticleController()

        @html
        def index(self):
            yield 'Index'

        @json(verbs='post')
        def login(self):
            return ["token"]

        @html(verbs=['get', 'post'])
        def contact(self, contact_id: int=None):
            yield "Contact: %s" % contact_id

        @html
        def users(self, user_id: int=None, attr: str=None):
            yield 'User: %s\n' % user_id
            yield 'Attr: %s\n' % attr

        @html
        def bad(self):
            raise Exception()

        @text
        def empty(self):
            pass

    def test_root(self):
        self.assert_get('/', expected_response='Index')
        self.assert_get('/index', expected_response='Index')

    def test_arguments(self):
        self.assert_get('/contact/1', expected_response='Contact: 1')
        self.assert_post('/contact', expected_response='Contact: None')
        self.assert_get('/users', expected_response='User: None\nAttr: None\n')
        self.assert_get('/users/10/')
        self.assert_get('/users/10/jobs', expected_response='User: 10\nAttr: jobs\n')
        self.assert_get('/users/10/11/11', status=404)
        self.assert_post('/articles/2', status=404)

    def test_verbs(self):
        self.assert_put('/', expected_response='Index')
        self.assert_post('/login', expected_response='[\n    "token"\n]')
        self.assert_get('/contact/test', expected_response='Contact: test')
        self.assert_post('/contact', expected_response='Contact: None')
        self.assert_put('/contact', status=405)
        self.assert_options('/contact', status=405)
        self.assert_options('/')
        self.assert_delete('/articles', status=405)

    def test_rest_controller(self):
        self.assert_get('/articles', expected_response='GET Articles')
        self.assert_get('/articles/23', expected_response='GET Article: 23')
        self.assert_post('/articles', expected_response='POST Article')
        self.assert_put('/articles/23', expected_response='PUT Article: 23')
        self.assert_put('/articles/23/links/2', expected_response='Article: 23, Links index: 2')
        self.assert_get('/articles/links', expected_response='Link1, Link2, Link3')
        self.assert_request('/articles', 'disallowed', status=404)
        self.assert_get('/articles/disallowed', status=404)

    def test_trailing_slash(self):
        self.assert_get('/users/10/jobs/', expected_response='User: 10\nAttr: jobs\n')

    def test_exception(self):
        self.assert_get('/bad', status=500)

    def test_empty_response(self):
        self.assert_get('/empty', expected_response='')

    def test_detect_verb_by_header(self):
        self.assert_post(
            '/articles/23',
            headers={
                'X-HTTP-VERB': 'put'
            },
            expected_response='PUT Article: 23'
        )


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
