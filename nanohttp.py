
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

import pymlconf


__version__ = '0.1.0-dev.11'

DEFAULT_CONFIG_FILE = 'nanohttp.yaml'
DEFAULT_ADDRESS = '8080'
BUILTIN_CONFIG = """
debug: true
"""


class HttpStatus(Exception):
    status_code = None
    status_text = None
    info = None

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


class HttpRedirect(HttpStatus):

    def __init__(self, location, *args, **kw):
        context.response_headers.add_header('Location', location)
        super().__init__(*args, **kw)


class HttpMovedPermanently(HttpRedirect):
    status_code, status_text, info = 301, 'Moved Permanently', 'Object moved permanently -- see URI list'


class HttpFound(HttpRedirect):
    status_code, status_text, info = 302, 'Found', 'Object moved temporarily -- see URI list'


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


class Context(object):
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
        if not hasattr(thread_local, 'nanohttp_context'):
            raise ContextIsNotInitializedError("Context is not initialized yet.")
        return thread_local.nanohttp_context

    @LazyAttribute
    def method(self):
        return self.environ['REQUEST_METHOD'].lower()

    @LazyAttribute
    def path(self):
        return self.environ['PATH_INFO']

    @LazyAttribute
    def request_uri(self):
        return wsgiref.util.request_uri(self.environ, include_query=True)

    @LazyAttribute
    def request_scheme(self):
        return wsgiref.util.guess_scheme(self.environ)

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

        if storage.list is None or not len(storage.list):
            return {}

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

    def __new__(cls):
        type_proxy = type('ContextProxy', (object, ), {
            '__getattr__': cls.__getattr__,
            '__setattr__': cls.__setattr__,
        })
        return object.__new__(type_proxy)

    def __getattr__(self, key):
        return getattr(Context.get_current(), key)

    def __setattr__(self, key, value):
        setattr(Context.get_current(), key, value)


def action(*a, methods='any', encoding='utf8', content_type=None):
    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods

        if encoding:
            func.__response_encoding__ = encoding

        if content_type:
            func.__content_type__ = content_type

        return func

    return _decorator(a[0]) if len(a) == 1 and callable(a[0]) else _decorator


html = functools.partial(action, content_type='text/html')
text = functools.partial(action, content_type='text/plain')
json = functools.partial(action, content_type='application/json')
xml = functools.partial(action, content_type='application/xml')


class Controller(object):
    http_methods = 'any'
    __response_encoding__ = 'utf8'
    __default_action__ = 'index'
    __remove_trailing_slash__ = True

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def load_app(self, config=None, config_files=None):
        print("Loading Configuration")
        settings.load(builtin=BUILTIN_CONFIG, init_value=config, files=config_files, force=True)
        self._hook('app_load')
        return self._handle_request

    def _handle_exception(self, ex):
        context.response_content_type = 'text/plain'
        context.response_encoding = 'utf8'
        if isinstance(ex, HttpStatus):
            return ex.status, ex.render()
        else:
            traceback.print_exc()
            error_page = self._hook('request_error', ex)
            e = InternalServerError(sys.exc_info())
            return e.status, e.render() if settings.debug else e.info if error_page is None else error_page


    def _handle_request(self, environ, start_response):
        ctx = Context(environ)
        ctx.__enter__()
        # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

        status = '200 OK'
        buffer = None

        try:
            self._hook('begin_request')
            if self.__remove_trailing_slash__:
                ctx.path = ctx.path.rstrip('/')
            resp_generator = iter(self(*ctx.path[1:].split('/')))
            buffer = next(resp_generator)

        except Exception as ex:
            status, resp_generator = self._handle_exception(ex)

        finally:
            self._hook('begin_response')
            start_response(status, ctx.response_headers.items())

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
            path = self.__default_action__
        else:
            path = self.__default_action__ if remaining_paths[0] == '' else remaining_paths[0]
            remaining_paths = remaining_paths[1:]

        handler = getattr(self, path, None)
        if handler is None or not hasattr(handler, 'http_methods') \
                or (hasattr(handler, '__code__') and handler.__code__.co_argcount-1 != len(remaining_paths)):
            raise HttpNotFound()

        if 'any' not in handler.http_methods and context.method not in handler.http_methods:
            raise HttpMethodNotAllowed()

        if hasattr(handler, '__response_encoding__'):
            context.response_encoding = handler.__response_encoding__

        if hasattr(handler, '__content_type__'):
            context.response_content_type = handler.__content_type__

        try:
            return handler(*remaining_paths)
        except TypeError as ex:
            raise HttpNotFound(str(ex))



class Static(Controller):
    __response_encoding__ = None
    __chunk_size__ = 0x4000
    __datetime_format__ = '%a, %m %b %Y %H:%M:%S GMT'

    def __init__(self, directory='.'):
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
            context.response_headers.add_header('Last-Modified', time.strftime(self.__datetime_format__, time.gmtime(stat.st_mtime)))

            with f:
                while True:
                    r = f.read(self.__chunk_size__)
                    if not r:
                        break
                    yield r

        except OSError:
            raise HttpNotFound()


def quickstart(controller=None, host='localhost',  port=8080, block=True, **kwargs):
    from wsgiref.simple_server import make_server

    if controller is None:
        from wsgiref.simple_server import demo_app
        app = demo_app
    else:
        app = controller.load_app(**kwargs)

    httpd = make_server(host, port, app)

    print("Serving http://%s:%d" % (host or 'localhost', port))
    if block:  # pragma: no cover
        httpd.serve_forever()
    else:
        t = threading.Thread(target=httpd.serve_forever, daemon=True)
        t.start()

        def shutdown():
            httpd.shutdown()
            httpd.server_close()
            t.join()


        return shutdown


def _load_controller_from_file(specifier, search_path):
    import importlib.util
    controller = None

    if specifier:
        module_name, class_name = specifier.split(':') if ':' in specifier else (specifier, 'Root')

        if module_name.endswith('.py'):
            module_name = module_name[:-3]

        spec = importlib.util.spec_from_file_location(module_name, location=join(search_path, '%s.py' % module_name))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        controller = getattr(module, class_name)()

    return controller


def _bootstrap(args, config_files=None, **kwargs):
    host, port = args.bind.split(':') if ':' in args.bind else ('', args.bind)

    controller = _load_controller_from_file(args.controller, args.directory)

    config_files = config_files or []
    config_files = [config_files] if isinstance(config_files, str) else config_files
    if args.config_file:
        config_files.extend(args.config_file)

    return quickstart(controller=controller, host=host, port=int(port), config_files=config_files, **kwargs)


def _cli_args(argv):
    import argparse

    parser = argparse.ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-c', '--config-file', action='append', default=[], help='This option may be passed multiple '
                                                                                 'times.')
    parser.add_argument('-b', '--bind', default=DEFAULT_ADDRESS, metavar='{HOST:}PORT', help='Bind Address. default: '
                                                                                             '%s' % DEFAULT_ADDRESS)
    parser.add_argument('-d', '--directory', default='.', help='The path to search for the python module, which '
                                                               'contains the controller class. default is: `.`')
    parser.add_argument('-V', '--version', default=False, action='store_true', help='Show the version.')
    parser.add_argument('controller', nargs='?', metavar='MODULE{.py}{:CLASS}',
                        help='The python module and controller class to launch. default is python built-in\'s : '
                             '`demo_app`, And the default value for `:CLASS` is `:Root` if omitted.')

    return parser.parse_args(argv[1:])


def main(argv=None):
    args = _cli_args(argv or sys.argv)

    if args.version:  # pragma: no cover
        print(__version__)
        return 0

    try:
        _bootstrap(args)
    except KeyboardInterrupt:  # pragma: no cover
        print('CTRL+C detected.')
        return -1
    else:  # pragma: no cover
        return 0


thread_local = threading.local()
context = ContextProxy()
settings = pymlconf.DeferredConfigManager()


__all__ = [
    'HttpStatus',
    'HttpBadRequest',
    'HttpUnauthorized',
    'HttpForbidden',
    'HttpNotFound',
    'HttpMethodNotAllowed',
    'HttpConflict',
    'HttpGone',
    'HttpMovedPermanently',
    'HttpFound',
    'InternalServerError',
    'Controller',
    'Static',
    'action',
    'html',
    'text',
    'json',
    'xml',
    'quickstart',
    'main',
    'context',
    'settings'
]


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())

