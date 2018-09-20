import cgi
import threading

import pymlconf
import ujson

from . import exceptions
from .configuration import settings, configure


class LazyAttribute:
    """ ``LazyAttribute`` decorator is intended to promote a
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
        if obj is None:
            return f
        val = f(obj)
        setattr(obj, f.__name__, val)
        return val


def quickstart(controller=None, application=None, host='localhost', port=8080,
               block=True, config=None):
    from wsgiref.simple_server import make_server

    try:
        settings.debug
    except pymlconf.ConfigurationNotInitializedError:
        configure()

    if config:
        settings.merge(config)

    if application is not None:
        app = application
    elif controller is None:
        from wsgiref.simple_server import demo_app
        app = demo_app
    else:
        from nanohttp.application import Application
        app = Application(root=controller)

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


def get_cgi_field_value(field):
    # noinspection PyProtectedMember
    return field.value if isinstance(field, cgi.MiniFieldStorage) \
        or (isinstance(field, cgi.FieldStorage) and not field._binary_file) \
        else field


def parse_any_form(environ, content_length=None, content_type=None):
    if content_type == 'application/json':
        if content_length is None:
            raise exceptions.HTTPBadRequest('Content-Length required')

        fp = environ['wsgi.input']
        data = fp.read(content_length)
        try:
            return ujson.decode(data)
        except (ValueError, TypeError):
            raise exceptions.HTTPBadRequest('Cannot parse the request')

    try:
        storage = cgi.FieldStorage(
            fp=environ['wsgi.input'],
            environ=environ,
            strict_parsing=False,
            keep_blank_values=True
        )
    except (TypeError, ValueError):
        raise exceptions.HTTPBadRequest('Cannot parse the request')

    result = {}
    if storage.list is None or not len(storage.list):
        return result

    for k in storage:
        v = storage[k]

        if isinstance(v, list):
            result[k] = [get_cgi_field_value(i) for i in v]
        else:
            result[k] = get_cgi_field_value(v)

    return result
