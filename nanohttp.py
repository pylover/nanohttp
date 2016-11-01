
import sys
import traceback
import cgi
import threading
import wsgiref.util
import wsgiref.headers
from urllib.parse import parse_qs


__version__ = '0.1.0-dev.0'


class HttpStatus(Exception):
    status_code = None
    status_text = None

    def __init__(self, message=None):
        super().__init__(message or self.status_text)

    @property
    def status(self):
        return '%s %s' % (self.status_code, self.status_text)

    def render(self):
        yield self.status


class HttpBadRequest(HttpStatus):
    status_code = 400
    status_text = 'Bad request'


class HttpUnauthorized(HttpStatus):
    status_code = 401
    status_text = 'You need to be authenticated'


class HttpForbidden(HttpStatus):
    status_code = 403
    status_text = 'Access denied'


class HttpNotFound(HttpStatus):
    status_code = 404
    status_text = 'Not Found'


class HttpConflict(HttpStatus):
    status_code = 409
    status_text = 'Conflict'


class HttpGone(HttpStatus):
    status_code = 410
    status_text = 'Access to resource is no longer available. Please contact us to find the reason.'


class HttpMethodNotAllowed(HttpStatus):
    status_code = 405
    status_text = 'Method not allowed'


class InternalServerError(HttpStatus):
    status_code = 500
    status_text = 'Internal server error'

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def render(self):
        from traceback import format_tb
        e_type, e_value, tb = self.exc_info
        yield 'Traceback (most recent call last):'
        yield from format_tb(tb)
        yield '%s: %s' % (e_type.__name__, e_value)


class ObjectIsNotInitializedError(Exception):
    pass


class ObjectProxy(object):
    """
    A simple object proxy to let deferred object's initialize later (for example: just after import):
    This class encapsulates some tricky codes to resolve the proxied object members using the
    `__getattribute__` and '__getattr__'. SO TAKE CARE about modifying the code, to prevent
    infinite loops and stack-overflow situations.

    Module: fancy_module

        deferred_object = None  # Will be initialized later.
        def init():
            global deferred_object
            deferred_object = AnyValue()
        proxy = ObjectProxy(lambda: deferred_object)

    In another module:

        from fancy_module import proxy, init
        def my_very_own_function():
            try:
                return proxy.any_attr_or_method()
            except: ObjectIsNotInitializedError:
                init()
                return my_very_own_function()

    """

    def __init__(self, resolver):
        object.__setattr__(self, '_resolver', resolver)

    @property
    def proxied_object(self):
        o = object.__getattribute__(self, '_resolver')()
        # if still is none, raise the exception
        if o is None:
            raise ObjectIsNotInitializedError("Configuration manager object is not initialized yet.")
        return o

    def __getattr__(self, key):
        return getattr(object.__getattribute__(self, 'proxied_object'), key)

    def __setattr__(self, key, value):
        setattr(object.__getattribute__(self, 'proxied_object'), key, value)


class LazyAttribute(object):
    """ ``attribute`` decorator is intended to promote a
        function call to object attribute. This means the
        function is called once and replaced with
        returned value.

        >>> class A:
        ...     def __init__(self):
        ...         self.counter = 0
        ...     @LazyAttribute
        ...     def count(self):
        ...         self.counter += 1
        ...         return self.counter
        >>> a = A()
        >>> a.count
        1
        >>> a.count
        1
    """
    __slots__ = ('f', )

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, t=None):
        f = self.f
        val = f(obj)
        setattr(obj, f.__name__, val)
        return val


class Context(dict):
    response_encoding = 'utf8'

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.headers = wsgiref.headers.Headers()

    def __enter__(self):
        thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del thread_local.nanohttp_context

    @property
    def response_content_type(self):
        return self.headers.get('Content-Type')

    @response_content_type.setter
    def response_content_type(self, v):
        self.headers['Content-Type'] = v

    @classmethod
    def get_current(cls):
        return thread_local.nanohttp_context

    @LazyAttribute
    def method(self):
        return self.environ['REQUEST_METHOD'].lower()

    @property
    def path(self):
        return self.environ['PATH_INFO']

    @LazyAttribute
    def uri(self):
        return wsgiref.util.request_uri(self.environ, include_query=True)

    @LazyAttribute
    def scheme(self):
        return wsgiref.util.guess_scheme(self.environ)

    @LazyAttribute
    def request_encoding(self):
        raise NotImplementedError

    @LazyAttribute
    def query_string(self):
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
            self.environ['QUERY_STRING'],
            keep_blank_values=True,
            strict_parsing=False
        ).items()}

    @LazyAttribute
    def form(self):
        result = {}

        storage = cgi.FieldStorage(
            fp=self.environ['wsgi.input'],
            environ=self.environ,
            keep_blank_values=True
        )

        def get_value(f):
            # noinspection PyProtectedMember
            return f.value if isinstance(f,  cgi.MiniFieldStorage) \
                              or (isinstance(f, cgi.FieldStorage) and not f._binary_file) else f

        for k in storage:

            v = storage[k]

            if isinstance(v, list):
                result[k] = [get_value(i) for i in v]
            else:
                result[k] = get_value(v)

        return result


def action(methods='any', encoding='utf8', content_type='text/plain'):
    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods

        if encoding.replace('-', '').lower() != 'utf8':
            func.http_encoding = encoding

        if content_type:
            func.content_type = content_type

        return func

    return _decorator


class Controller(object):
    http_methods = 'any'
    http_encoding = 'utf8'
    default_action = 'index'

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def load_app(self):
        self._hook('app_load')
        return self._handle_request

    def _handle_request(self, environ, start_response):
        ctx = Context(environ)
        ctx.__enter__()
        # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

        status = '200 OK'
        buffer = None

        try:
            self._hook('begin_request')
            # for chunk in self(*context.path[1:].split('/')):
            #     yield chunk
            resp_generator = iter(self(*ctx.path[1:].split('/')))
            buffer = next(resp_generator)

        except HttpStatus as ex:
            status = ex.status
            resp_generator = iter(ex.render())

        except Exception as ex:
            # FIXME: Handle exception !
            # Giving a chance to get better output on error.
            error_page = self._hook('request_error', ex)
            e = InternalServerError(sys.exc_info())
            status = e.status
            resp_generator = iter(e.render() if error_page is None else error_page)
            traceback.print_exc()

        finally:
            start_response(status, ctx.headers.items())
            self._hook('begin_response')

        def _response():
            try:
                if buffer is not None:
                    yield buffer.encode(ctx.response_encoding)

                for chunk in resp_generator:
                    yield chunk.encode(ctx.response_encoding)

            finally:
                self._hook('end_response')
                context.__exit__(*sys.exc_info())

        return _response()


    def __call__(self, *remaining_paths):
        """
        Dispatcher
        :param path:
        :param remaining_paths:
        :return:
        """

        if not len(remaining_paths):
            path = self.default_action
        else:
            path = self.default_action if remaining_paths[0] == '' else remaining_paths[0]
            remaining_paths = remaining_paths[1:]

        handler = getattr(self, path, None)
        if handler is None \
                or not hasattr(handler, 'http_methods') \
                or (hasattr(handler, '__code__') and handler.__code__.co_argcount - 1 != len(remaining_paths)):
            raise HttpNotFound()

        if 'any' not in handler.http_methods and context.method not in handler.http_methods:
            raise HttpMethodNotAllowed()

        if hasattr(handler, 'http_encoding'):
            context.response_encoding = handler.http_encoding

        if hasattr(handler, 'content_type'):
            context.response_content_type = handler.content_type

        return handler(*remaining_paths)


def quickstart(controller=None, host='localhost',  port=8080):
    from wsgiref.simple_server import make_server

    if controller is None:
        from wsgiref.simple_server import demo_app
        app = demo_app
    else:
        app = controller.load_app()

    httpd = make_server(host, port, app)
    try:
        print("Serving http://%s:%d" % (host or 'localhost', port))
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('CTRL+C Detected !')


class Demo(Controller):

    @action()
    def index(self):
        yield from ('%s: %s\n' % i for i in context.environ.items())


def main():
    import argparse
    import importlib.util
    from os.path import basename, join

    parser = argparse.ArgumentParser(prog=basename(sys.argv[0]))
    parser.add_argument('-c', '--config-file', default=DEFAULT_CONFIG_FILE, help='Default: %s' % DEFAULT_CONFIG_FILE)
    parser.add_argument('-b', '--bind', default=DEFAULT_ADDRESS, metavar='{HOST:}PORT', help='Bind Address. default: '
                                                                                             '%s' % DEFAULT_ADDRESS)
    parser.add_argument('-d', '--directory', default='.', help='The path to search for the python module, which '
                                                               'contains the controller class. default is: `.`')
    parser.add_argument('-V', '--version', default=False, action='store_true', help='Show the version.')
    parser.add_argument('controller', nargs='?', default=DEFAULT_APP, metavar='MODULE{:CLASS}',
                        help='The python module and controller class to launch. default: '
                             '`%s`, And the default value for `:CLASS` is `:Root` if omitted.' % DEFAULT_APP)

    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0

    host, port = args.bind.split(':') if ':' in args.bind else ('',  args.bind)
    module_name, class_name = args.controller.split(':') if ':' in args.controller else (args.controller, 'Root')
    spec = importlib.util.spec_from_file_location(module_name, location=join(args.directory, '%s.py' % module_name))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # noinspection PyBroadException
    try:
        quickstart(getattr(module, class_name)(), host=host, port=int(port))
    except:
        traceback.print_exc()
        return 1
    else:
        return 0


DEFAULT_CONFIG_FILE = 'nanohttp.yaml'
DEFAULT_ADDRESS = '8080'
DEFAULT_APP = 'nanohttp:Demo'

thread_local = threading.local()
context = ObjectProxy(Context.get_current)


if __name__ == '__main__':
    sys.exit(main())


