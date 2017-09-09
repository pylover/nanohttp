import ujson
import functools

from .configuration import settings
from .contexts import context


def action(*args, verbs='any', encoding='utf-8', content_type=None, inner_decorator=None, **kwargs):
    def decorator(func):
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
        return decorator(f)

    return decorator


def jsonify(func):

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


def ifmatch(tag):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context.etag_match(tag() if callable(tag) else tag)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def etag(*args, tag=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            _etag = tag() if callable(tag) else tag
            if _etag is not None:
                context.etag_none_match(_etag)
                return func(*a, **kw)
            else:
                result = func(*a, **kw)
                if hasattr(result, '__etag__'):
                    _etag = result.__etag__
                if _etag:
                    context.etag_none_match(_etag)
                return result
        return wrapper

    if args and callable(args[0]):
        return decorator(args[0])

    return decorator
