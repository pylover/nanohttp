
import unittest

from nanohttp import Controller, html, json, RestController, text, RegexRouteController
from nanohttp.tests.helpers import WsgiAppTestCase


class LinksController(Controller):

    @html
    def index(self, article_id: int=None, link_id: int=None):
        if link_id:
            yield 'Article: %s, Links index: %s' % (article_id, link_id)
        else:
            yield 'Link1, Link2, Link3'


class ArticleController(RestController):
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

    @text
    def remove(self, id_: int):
        yield 'Removing, %s' % id_


class AwesomeRegexController(RegexRouteController):

    def __init__(self):
        super().__init__([
            ('/awesome/(?P<name>\d+)', self.awesome_action)
        ])

    @text
    def awesome_action(self, name):
        return name


class DispatcherTestCase(WsgiAppTestCase):

    class Root(Controller):

        articles = ArticleController()
        regex = AwesomeRegexController()

        @html
        def index(self):
            yield 'Index'

        @json(verbs='post')
        def login(self):
            return ['token']

        @html(verbs=['get', 'post'])
        def contact(self, contact_id: int=None):
            yield 'Contact: %s' % contact_id

        @html
        def users(self, user_id: int=None, attr: str=None):
            yield 'User: %s\n' % user_id
            yield 'Attr: %s\n' % attr

        @html
        def books(self, name=None, *, sort='user_id', filters=None):
            yield 'name: %s sort: %s filters: %s' % (name, sort, filters)

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

    def test_positional_argument_dispatch(self):
        self.assert_request('/articles/23', 'remove', expected_response='Removing, 23')

    def test_dispatch_query_string(self):
        self.assert_get('/books', expected_response='name: None sort: user_id filters: None')
        self.assert_get('/books/C++', expected_response='name: C++ sort: user_id filters: None')
        self.assert_get('/books?sort=title', expected_response='name: None sort: title filters: None')
        self.assert_get(
            '/books/?filters=a>1&filters=b<3',
            expected_response='name: None sort: user_id filters: [\'a>1\', \'b<3\']'
        )

    def test_regex_route_controller(self):
        self.assert_get('/regex/awesome/badinteger', status=404)
        self.assert_get('/regex/awesome/123', expected_response='123')


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
