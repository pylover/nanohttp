import ujson
import functools

from .configuration import settings


def action(*args, verbs='any', encoding='utf-8', content_type=None, inner_decorator=None, **kwargs):
    def _decorator(func):
        argcount = func.__code__.co_argcount

        if inner_decorator is not None:
            func = inner_decorator(func, *args, **kwargs)

        func.__http_methods__ = verbs
        func.__response_encoding__ = encoding
        func.__argcount__ = argcount

        if content_type:
            func.__content_type__ = content_type

        return func

    if args and callable(args[0]):
        f = args[0]
        args = tuple()
        return _decorator(f)
    else:
        return _decorator


def jsonify(func, *a, **kw):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        elif not isinstance(result, (list, dict, int, str)):
            raise ValueError('Cannot encode to json: %s' % type(result))

        return ujson.dumps(result, indent=settings.json.indent)

    return wrapper


html = functools.partial(action, content_type='text/html')
text = functools.partial(action, content_type='text/plain')
json = functools.partial(action, content_type='application/json', inner_decorator=jsonify)
xml = functools.partial(action, content_type='application/xml')
binary = functools.partial(action, content_type='application/octet-stream', encoding=None)
