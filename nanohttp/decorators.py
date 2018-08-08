import functools
from inspect import signature, Parameter
from typing import Union

import ujson

from .contexts import context


def action(*args, verbs: Union[str, list, tuple]='any', encoding: str='utf-8',
           content_type: Union[str, None]=None,
           inner_decorator: Union[callable, None]=None,
           prevent_empty_form=None, prevent_form=None, **kwargs):
    """
    Base action decorator

    Marks the function as a nanohttp handler/action.

    :param verbs: Allowed HTTP methods
    :param encoding: Content encoding
    :param content_type: Response Content Type
    :param inner_decorator: Inner decorator, to put it between this decorator
                            and the handler.
    :param prevent_empty_form: Boolean or str, indicates to prevent empty HTTP
                               form. if str given, a
                               :class:`.HTTPStatus(<str>)` will be raised.
                               otherwise :class:`.HTTPBadRequest`.
    :param prevent_form: Boolean or str, indicates to prevent any HTTP form. if
                         str given, a :class:`.HTTPStatus(<str>)` will be
                         raised, otherwise :class:`.HTTPBadRequest`.

    """
    def decorator(func):
        nonlocal verbs

        if inner_decorator is not None:
            func = inner_decorator(func, *args, **kwargs)

        # Examining the signature,
        # and counting the optional and positional arguments.
        positional_arguments, optional_arguments, keywordonly_arguments = \
            [], [], []
        action_signature = signature(func)
        for name, parameter in action_signature.parameters.items():
            if name == 'self':
                continue

            if parameter.kind == Parameter.KEYWORD_ONLY:
                keywordonly_arguments.append(
                    (parameter.name, parameter.default)
                )
            elif parameter.default is Parameter.empty:
                positional_arguments.append(parameter.name)
            else:
                optional_arguments.append((parameter.name, parameter.default))

        if isinstance(verbs, str):
            verbs = [verbs]

        func.__nanohttp__ = dict(
            verbs=verbs,
            encoding=encoding,
            content_type=content_type,
            positional_arguments=positional_arguments,
            optional_arguments=optional_arguments,
            keywordonly_arguments=keywordonly_arguments,
            prevent_empty_form=prevent_empty_form,
            prevent_form=prevent_form,
            default_action='index'
        )

        return func

    if args and callable(args[0]):
        f = args[0]
        args = tuple()
        return decorator(f)

    return decorator


def chunked(trailer_field=None, trailer_value=None):
    """Enables chunked encoding on an action
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal trailer_field, trailer_value
            context.response_headers.add_header('Transfer-Encoding', 'chunked')
            if trailer_field:
                context.response_headers.add_header('Trailer', trailer_field)
            result = func(*args, **kwargs)
            try:
                while True:
                    chunk = next(result)
                    yield f'{len(chunk)}\r\n{chunk}\r\n'

            except StopIteration:
                yield '0\r\n'
                if trailer_field and trailer_value:
                    yield f'{trailer_field}: {trailer_value}\r\n'
                yield '\r\n'

            except Exception as ex:
                yield str(ex)
                yield '0\r\n'
                yield '\r\n'

        return wrapper

    if callable(trailer_field):
        func = trailer_field
        trailer_field = None
        return decorator(func)

    return decorator


def jsonify(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        elif not isinstance(result, (list, dict, int, str)):
            raise ValueError('Cannot encode to json: %s' % type(result))

        return ujson.dumps(result, indent=4)

    return wrapper


#: HTML action decorator
html = functools.partial(action, content_type='text/html')

#: Plain Text action decorator
text = functools.partial(action, content_type='text/plain')

#: JSON action decorator
#:
#: accepts list, dict, int, str or objects have ``to_dict`` method.
json = functools.partial(
    action,
    content_type='application/json',
    inner_decorator=jsonify
)

#: XML action decorator
xml = functools.partial(action, content_type='application/xml')

#: Binary-data action decorator
binary = functools.partial(
    action,
    content_type='application/octet-stream',
    encoding=None
)


def ifmatch(tag: Union[str, int, callable]):
    """ Validate ``If-Match`` header with given tag argument """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            context.etag_match(tag() if callable(tag) else tag)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def etag(*args, tag: Union[str, int, callable, None]=None):
    """Validate ``If-None-Match`` and response with ``ETag`` header

    tag is getting from ``tag`` argument or response object ``__etag__``
     attribute
    """
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
