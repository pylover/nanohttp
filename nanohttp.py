
import time
import os
import sys
import cgi
import functools
import traceback
import threading
import wsgiref.util
import wsgiref.headers
from datetime import datetime
from os.path import isdir, join, relpath, pardir, basename, exists
from mimetypes import guess_type
from urllib.parse import parse_qs

import pymlconf
import ujson


__version__ = '0.1.0'

DEFAULT_CONFIG_FILE = 'nanohttp.yml'
DEFAULT_ADDRESS = '8080'
HTTP_DATETIME_FORMAT = '%a, %m %b %Y %H:%M:%S GMT'
BUILTIN_CONFIG = """
debug: true
domain:
cookie:
  http_only: false
  secure: false
json:
  indent: 4
"""


class HttpStatus(Exception):
    status_code = None
    status_text = None
    info = None

    def __init__(self, message=None):
        super().__init__(message or self.status_text)

    @property
    def status(self):
        return '%s %s' % (self.status_code, self)

    def render(self):
        return self.status


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
        return 'Traceback (most recent call last):\n%s\n%s: %s' % (
            ''.join(format_tb(tb)),
            e_type.__name__,
            e_value
        )


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


class HttpCookie(object):
    """
    HTTP Cookie
    http://www.ietf.org/rfc/rfc2109.txt

    ``domain``, ``secure`` and ``http_only`` are taken from ``config`` if not set.
    """
    __slots__ = ('name', 'value', 'path', 'expires',
                 'domain', 'secure', 'http_only')

    def __init__(self, name, value=None, path='/', expires=None, max_age=None, domain=None, secure=None,
                 http_only=None):
        self.name = name
        self.value = value
        self.path = path
        if max_age is None:
            self.expires = expires
        else:
            self.expires = datetime.utcfromtimestamp(time.time() + max_age)
        if domain is None:
            self.domain = settings.domain
        else:
            self.domain = domain
        if secure is None:
            self.secure = settings.cookie.secure
        else:
            self.secure = secure
        if http_only is None:
            self.http_only = settings.cookie.http_only
        else:
            self.http_only = http_only

    @classmethod
    def delete(cls, name, path='/', domain=None, options=None):
        """ Returns a cookie to be deleted by browser.
        """
        return cls(name,
                   expires='Sat, 01 Jan 2000 00:00:01 GMT',
                   path=path, domain=domain, options=options)

    def http_set_cookie(self):
        """ Returns Set-Cookie response header.
        """
        directives = []
        append = directives.append
        append(self.name + '=')
        if self.value:
            append(self.value)
        if self.domain:
            append('; domain=%s' % self.domain)
        if self.expires:
            append('; expires=%s' % self.expires.strftime(HTTP_DATETIME_FORMAT))
        if self.path:
            append('; path=%s' % self.path)
        if self.secure:
            append('; secure')
        if self.http_only:
            append('; httponly')
        return 'Set-Cookie', ''.join(directives)


# FIXME: use __slots__
class Context(object):
    response_encoding = None

    def __init__(self, environ):
        super(Context, self).__init__()
        self.environ = environ
        self.response_headers = wsgiref.headers.Headers()
        self.response_cookies = []

    def __enter__(self):
        thread_local.nanohttp_context = self
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del thread_local.nanohttp_context
        # for attr in ('environ', 'response_headers', 'response_cookies', 'method', 'path', 'request_uri',
        #              'request_scheme', 'query_string', 'form', 'cookies'):
        #     if hasattr(self, attr):
        #         delattr(self, attr)

    @LazyAttribute
    def request_content_length(self):
        v = self.environ.get('CONTENT_LENGTH')
        return v if v is None else int(v)

    @LazyAttribute
    def request_content_type(self):
        content_type = self.environ.get('CONTENT_TYPE')
        if content_type:
            return content_type.split(';')[0]
        return None

    @property
    def response_content_type(self):
        content_type = self.response_headers.get('Content-Type')
        if content_type:
            return content_type.split(';')[0]
        return None

    @response_content_type.setter
    def response_content_type(self, v):
        self.response_headers['Content-Type'] = '%s; charset=%s' % (v, self.response_encoding)

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

        if self.request_content_type == 'application/json':
            fp = self.environ['wsgi.input']
            data = fp.read(self.request_content_length)
            return ujson.decode(data)

        storage = cgi.FieldStorage(
            fp=self.environ['wsgi.input'],
            environ=self.environ,
            strict_parsing=False,
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

    @LazyAttribute
    def cookies(self):
        if 'HTTP_COOKIE' in self.environ:
            return dict([pair.split('=', 1) for pair in self.environ['HTTP_COOKIE'].split('; ')]) or {}
        else:
            return {}

    def encode_response(self, buffer):
        if self.response_encoding:
            return buffer.encode(self.response_encoding)
        else:
            return buffer


class ContextProxy(Context):

    # noinspection PyInitNewSignature
    def __new__(cls) -> Context:
        type_proxy = type('ContextProxy', (object, ), {
            '__getattr__': cls.__getattr__,
            '__setattr__': cls.__setattr__,
        })
        # noinspection PyTypeChecker
        return object.__new__(type_proxy)

    def __getattr__(self, key):
        return getattr(Context.get_current(), key)

    def __setattr__(self, key, value):
        setattr(Context.get_current(), key, value)


def action(*verbs, encoding='utf-8', content_type=None, inner_decorator=None):
    def _decorator(func):

        # args_count = func.__code__.co_argcount
        if inner_decorator is not None:
            func = inner_decorator(func)

        # func.__args_count__ = args_count
        func.__http_methods__ = verbs if verbs else 'any'

        if encoding:
            func.__response_encoding__ = encoding

        if content_type:
            func.__content_type__ = content_type

        return func

    if verbs and callable(verbs[0]):
        f = verbs[0]
        verbs = tuple()
        return _decorator(f)
    else:
        return _decorator


def jsonify(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        elif not isinstance(result, (list, dict)):
            raise TypeError('Cannot encode to json: %s' % type(result))

        yield ujson.dumps(result, indent=settings.json.indent)

    return wrapper


html = functools.partial(action, content_type='text/html')
text = functools.partial(action, content_type='text/plain')
json = functools.partial(action, content_type='application/json', inner_decorator=jsonify)
xml = functools.partial(action, content_type='application/xml')


def configure(*args, **kwargs):
    print("Loading Configuration")
    settings.load(*args, builtin=BUILTIN_CONFIG, **kwargs)


class Controller(object):
    __http_methods__ = 'any'
    __response_encoding__ = 'utf8'
    __default_action__ = 'index'
    __remove_trailing_slash__ = True

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def load_app(self):
        self._hook('app_load')
        return self._handle_request

    def _handle_exception(self, ex):
        context.response_encoding = 'utf-8'

        error = ex if isinstance(ex, HttpStatus) else InternalServerError(sys.exc_info())
        error_page = self._hook('request_error', error)
        message = error.status_text
        description = error.render() if settings.debug else error.info if error_page is None else error_page

        if context.response_content_type == 'application/json':
            response = ujson.encode(dict(
                message=message,
                description=description
            ))
        else:
            context.response_content_type = 'text/plain'
            response = "%s\n%s" % (message, description)

        if isinstance(error, InternalServerError):
            traceback.print_exc()

        def resp():
            yield response

        return error.status, resp()

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

            result = self(*ctx.path.split('?')[0][1:].split('/'))
            if result:
                resp_generator = iter(result)
                buffer = next(resp_generator)
            else:
                resp_generator = None

        except Exception as ex:
            status, resp_generator = self._handle_exception(ex)

        finally:
            self._hook('begin_response')

            if context.response_cookies:
                for cookie in context.response_cookies:
                    ctx.response_headers.add_header(*cookie.http_set_cookie())
            start_response(status, ctx.response_headers.items())

        def _response():
            try:
                if buffer is not None:
                    yield ctx.encode_response(buffer)

                if resp_generator:
                    # noinspection PyTypeChecker
                    for chunk in resp_generator:
                        yield ctx.encode_response(chunk)

            finally:
                self._hook('end_response')
                context.__exit__(*sys.exc_info())

        return _response()

    # noinspection PyMethodMayBeStatic
    def _serve_handler(self, handler, *remaining_paths):
        if hasattr(handler, '__response_encoding__'):
            context.response_encoding = handler.__response_encoding__

        if hasattr(handler, '__content_type__'):
            context.response_content_type = handler.__content_type__

        try:
            return handler(*remaining_paths)
        except TypeError as ex:
            raise HttpNotFound(str(ex))

    def _dispatch(self, *remaining_paths):
        if not len(remaining_paths):
            path = self.__default_action__
        else:
            path = self.__default_action__ if remaining_paths[0] == '' else remaining_paths[0]
            remaining_paths = remaining_paths[1:]

        # Ensuring the handler
        handler = getattr(self, path, None)
        if handler is None:
            handler = getattr(self, self.__default_action__, None)
            if handler is not None:
                remaining_paths = (path, ) + remaining_paths

        if handler is None or not hasattr(handler, '__http_methods__') \
                or (hasattr(handler, '__annotations__') and len(handler.__annotations__) < len(remaining_paths)):
            raise HttpNotFound()

        if 'any' != handler.__http_methods__ and context.method not in handler.__http_methods__:
            raise HttpMethodNotAllowed()

        return handler, remaining_paths

    def __call__(self, *remaining_paths):
        handler, remaining_paths = self._dispatch(*remaining_paths)
        return self._serve_handler(handler, *remaining_paths)


class RestController(Controller):

    def _dispatch(self, *remaining_paths):

        if remaining_paths:
            first_path = remaining_paths[0]
            if hasattr(self, first_path):
                return getattr(self, first_path), remaining_paths[1:]

        if not hasattr(self, context.method):
            raise HttpMethodNotAllowed()

        handler = getattr(self, context.method)

        if hasattr(handler, '__annotations__') and len(handler.__annotations__) < len(remaining_paths):
            raise HttpNotFound()

        return handler, remaining_paths


class Static(Controller):
    __response_encoding__ = None
    __chunk_size__ = 0x4000

    def __init__(self, directory='.', default_document='index.html'):
        self.default_document = default_document
        self.directory = directory

    def __call__(self, *remaining_paths):

        # Find the physical path of the given path parts
        physical_path = join(self.directory, *remaining_paths)

        # Check to do not access the parent directory of root and also we are not listing directories here.
        if pardir in relpath(physical_path, self.directory):
            raise HttpForbidden()

        if isdir(physical_path):
            if self.default_document:
                physical_path = join(physical_path, self.default_document)
                if not exists(physical_path):
                    raise HttpForbidden
            else:
                raise HttpForbidden

        context.response_headers.add_header('Content-Type', guess_type(physical_path)[0] or 'application/octet-stream')

        try:
            f = open(physical_path, mode='rb')
            stat = os.fstat(f.fileno())
            context.response_headers.add_header('Content-Length', str(stat[6]))
            context.response_headers.add_header(
                'Last-Modified',
                time.strftime(HTTP_DATETIME_FORMAT, time.gmtime(stat.st_mtime))
            )

            with f:
                while True:
                    r = f.read(self.__chunk_size__)
                    if not r:
                        break
                    yield r

        except OSError:
            raise HttpNotFound()


def quickstart(controller=None, host='localhost',  port=8080, block=True, config=None):
    from wsgiref.simple_server import make_server

    if config:
        settings.merge(config)

    if controller is None:
        from wsgiref.simple_server import demo_app
        app = demo_app
    else:
        app = controller.load_app()

    port = int(port)
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


def _load_controller_from_file(specifier):
    import importlib.util
    controller = None

    if specifier:
        module_name, class_name = specifier.split(':') if ':' in specifier else (specifier, 'Root')

        if module_name:

            if module_name.endswith('.py'):
                module_name = module_name[:-3]

            spec = importlib.util.spec_from_file_location(module_name, location=join('%s.py' % module_name))
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            controller = getattr(module, class_name)()

        else:
            controller = globals()[class_name]()

    return controller


def _bootstrap(args, config_files=None, config_dirs=None, **kwargs):
    host, port = args.bind.split(':') if ':' in args.bind else ('', args.bind)

    # Change dir
    if relpath(args.directory, '.') != '.':
        os.chdir(args.directory)

    config_files = config_files or []
    config_files = [config_files] if isinstance(config_files, str) else config_files
    if args.config_file:
        config_files.extend(args.config_file)

    config_dirs = config_dirs or []
    config_dirs = [config_dirs] if isinstance(config_dirs, str) else config_dirs
    if args.config_directory:
        config_dirs.extend(args.config_directory)

    configure(files=config_files, dirs=config_dirs, force=True)

    return quickstart(
        controller=_load_controller_from_file(args.controller),
        host=host,
        port=int(port),
        **kwargs
    )


def _cli_args(argv):
    import argparse

    parser = argparse.ArgumentParser(prog=basename(argv[0]))
    parser.add_argument('-c', '--config-file', action='append', default=[], help='This option may be passed multiple '
                                                                                 'times.')
    parser.add_argument('-d', '--config-directory', action='append', default=[], help='This option may be passed '
                                                                                      'multiple times.')
    parser.add_argument('-b', '--bind', default=DEFAULT_ADDRESS, metavar='{HOST:}PORT', help='Bind Address. default: '
                                                                                             '%s' % DEFAULT_ADDRESS)
    parser.add_argument('-C', '--directory', default='.', help='Change to this path before starting the server '
                                                               'default is: `.`')
    parser.add_argument('-V', '--version', default=False, action='store_true', help='Show the version.')
    parser.add_argument('controller', nargs='?', metavar='{MODULE{.py}}{:CLASS}',
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
    'HttpCookie',
    'Controller',
    'RestController',
    'Static',
    'action',
    'html',
    'text',
    'json',
    'xml',
    'quickstart',
    'main',
    'context',
    'settings',
    'configure'
]


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
