
import time
import os
import sys
import cgi
import functools
import traceback
import threading
import wsgiref.util
import wsgiref.headers
from os.path import isdir, join, relpath, pardir, basename
from mimetypes import guess_type
from urllib.parse import parse_qs


__version__ = '0.1.0-dev.1'


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
    status_code, status_text, info = 400, 'Bad Request', 'Bad request syntax or unsupported method'


class HttpUnauthorized(HttpStatus):
    status_code, status_text, info = 401, 'Unauthorized', 'No permission -- see authorization schemes'


class HttpForbidden(HttpStatus):
    status_code, status_text, info = 403, 'Forbidden', 'Request forbidden -- authorization will not help'


class HttpNotFound(HttpStatus):
    status_code, status_text, info = 404, 'Not Found', 'Nothing matches the given URI'


class HttpMethodNotAllowed(HttpStatus):
    status_code, status_text, info = 405, 'Method Not Allowed', 'Specified method is invalid for this resource'


class HttpConflict(HttpStatus):
    status_code, status_text, info = 409, 'Conflict', 'Request conflict'


class HttpGone(HttpStatus):
    status_code, status_text, info = 410, 'Gone', 'URI no longer exists and has been permanently removed'


class HttpMovedPermanently(HttpStatus):
    status_code, status_text, info = 301, 'Moved Permanently', 'Object moved permanently -- see URI list'


class InternalServerError(HttpStatus):
    status_code, status_text, info = 500, 'Internal Server Error', 'Server got itself in trouble'

    def __init__(self, exc_info):
        self.exc_info = exc_info

    def render(self):
        from traceback import format_tb
        e_type, e_value, tb = self.exc_info
        yield 'Traceback (most recent call last):'
        yield from format_tb(tb)
        yield '%s: %s' % (e_type.__name__, e_value)


class ContextIsNotInitializedError(Exception):
    pass


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
    response_encoding = None

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.response_headers = wsgiref.headers.Headers()

    def __enter__(self):
        thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del thread_local.nanohttp_context

    @property
    def response_content_type(self):
        return self.response_headers.get('Content-Type')

    @response_content_type.setter
    def response_content_type(self, v):
        self.response_headers['Content-Type'] = v

    @classmethod
    def get_current(cls):
        try:
            return thread_local.nanohttp_context
        except AttributeError:
            raise ContextIsNotInitializedError("Context is not initialized yet.")

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

        if storage.list is None:
            return None

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


class ContextProxy(Context):

    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def __getattr__(self, key):
        return getattr(Context.get_current(), key)

    def __setattr__(self, key, value):
        setattr(Context.get_current(), key, value)


def action(*a, methods='any', encoding='utf8', content_type=None):
    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods

        if encoding:
            func.response_encoding = encoding

        if content_type:
            func.content_type = content_type

        return func

    return _decorator(a[0]) if len(a) == 1 and callable(a[0]) else _decorator


html = functools.partial(action, content_type='text/html')
text = functools.partial(action, content_type='text/plain')
json = functools.partial(action, content_type='application/json')
xml = functools.partial(action, content_type='application/xml')


class Controller(object):
    http_methods = 'any'
    response_encoding = 'utf8'
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
            resp_generator = iter(self(*ctx.path[1:].split('/')))
            buffer = next(resp_generator)

        except HttpStatus as ex:
            status = ex.status
            ctx.response_encoding = 'utf8'
            resp_generator = iter(ex.render())

        except Exception as ex:
            error_page = self._hook('request_error', ex)
            e = InternalServerError(sys.exc_info())
            status = e.status
            ctx.response_encoding = 'utf8'
            resp_generator = iter(e.render() if error_page is None else error_page)
            traceback.print_exc()

        finally:
            start_response(status, ctx.response_headers.items())
            self._hook('begin_response')

        def _response():
            try:

                if ctx.response_encoding:

                    if buffer is not None:
                        yield buffer.encode(ctx.response_encoding)

                    for chunk in resp_generator:
                        yield chunk.encode(ctx.response_encoding)

                else:
                    if buffer is not None:
                        yield buffer

                    for chunk in resp_generator:
                        yield chunk

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

        if hasattr(handler, 'response_encoding'):
            context.response_encoding = handler.response_encoding

        if hasattr(handler, 'content_type'):
            context.response_content_type = handler.content_type

        return handler(*remaining_paths)


class Static(Controller):
    response_encoding = None
    chunk_size = 0x4000
    datetime_format = '%a, %m %b %Y %H:%M:%S GMT'

    def __init__(self, directory):
        self.directory = directory

    def __call__(self, *remaining_paths):

        # Find the physical path of the given path parts
        physical_path = join(self.directory, *remaining_paths)

        # Check to do not access the parent directory of root and also we are not listing directories here.
        if isdir(physical_path) or pardir in relpath(physical_path, self.directory):
            raise HttpForbidden()

        context.response_headers.add_header('Content-Type', guess_type(physical_path)[0] or 'application/octet-stream')

        try:
            f = open(physical_path, mode='rb')
            stat = os.fstat(f.fileno())
            context.response_headers.add_header('Content-Length', str(stat[6]))
            context.response_headers.add_header('Last-Modified', time.strftime(self.datetime_format, time.gmtime(stat.st_mtime)))

            with f:
                while True:
                    r = f.read(self.chunk_size)
                    if not r:
                        break
                    yield r

        except OSError:
            raise HttpNotFound()


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
context = ContextProxy()


__all__ = [

]


if __name__ == '__main__':
    sys.exit(main())


