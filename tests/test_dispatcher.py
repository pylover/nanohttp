
import unittest

from nanohttp import Controller, html, json, RestController
from tests.helpers import WsgiAppTestCase


class LinksController(Controller):

    @html
    def index(self, article_id, link_id):
        yield 'Article: %s, Links index: %s' % (article_id, link_id)


class ArticleController(RestController):
    links = LinksController()

    def get(self, article_id=None):
        yield "GET Article%s" % (
            's' if not article_id else (': ' + article_id)
        )

    def post(self):
        yield "POST Article"

    def put(self, article_id=None, *remaining):
        if remaining:
            yield from self.links(article_id, *remaining[1:])
        else:
            yield "PUT Article: %s" % article_id


class DispatcherTestCase(WsgiAppTestCase):

    class Root(Controller):

        articles = ArticleController()

        @html
        def index(self):
            yield 'Index'

        @json('post')
        def login(self):
            return ["token"]

        @html('get', 'post')
        def contact(self, contact_id=None):
            yield "Contact: %s" % contact_id

        @html
        def users(self, user_id, attr=None):
            yield 'User: %s\n' % user_id
            yield 'Attr: %s\n' % attr

        @html
        def bad(self):
            raise Exception()

    def test_root(self):
        self.assert_get('/', expected_response='Index')
        self.assert_get('/index', expected_response='Index')

    def test_arguments(self):
        self.assert_get('/contact/1', expected_response='Contact: 1')
        self.assert_post('/contact', expected_response='Contact: None')
        self.assert_get('/users', status=404)
        self.assert_get('/users/10/')
        self.assert_get('/users/10/jobs', expected_response='User: 10\nAttr: jobs\n')
        self.assert_get('/users/10/11/11', status=404)

    def test_verbs(self):
        self.assert_put('/', expected_response='Index')
        self.assert_post('/login', expected_response='[\n    "token"\n]')
        self.assert_get('/contact/test', expected_response='Contact: test')
        self.assert_post('/contact', expected_response='Contact: None')
        self.assert_put('/contact', status=405)
        self.assert_options('/contact', status=405)
        self.assert_options('/')

    def test_rest_controller(self):
        self.assert_get('/articles', expected_response='GET Articles')
        self.assert_get('/articles/23', expected_response='GET Article: 23')
        self.assert_post('/articles', expected_response='POST Article')
        self.assert_put('/articles/23', expected_response='PUT Article: 23')
        self.assert_put('/articles/23/links/2', expected_response='Article: 23, Links index: 2')

    def test_trailing_slash(self):
        self.assert_get('/users/10/jobs/', expected_response='User: 10\nAttr: jobs\n')

    def test_exception(self):
        self.assert_get('/bad', status=500)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
