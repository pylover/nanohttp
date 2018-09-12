import functools
from inspect import signature, Parameter
from typing import Union

import ujson

from .contexts import context
from .constants import UNLIMITED


def action(*args, verbs='any', encoding='utf-8', content_type=None,
           inner_decorator=None, prevent_empty_form=None, prevent_form=None,
           form_whitelist=None, **kwargs):
    """
    Base action decorator

    Marks the function as a nanohttp handler/action.

    :param verbs: Allowed HTTP methods as list or tuple of strings.
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
    :param form_whitelist: A list of allowed form fields. or a
                           tuple(list, httpstatus)
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
        positional_unlimited = False
        optional_unlimited = False

        for name, parameter in action_signature.parameters.items():
            if name == 'self':
                continue

            if parameter.kind == Parameter.KEYWORD_ONLY:
                keywordonly_arguments.append(
                    (parameter.name, parameter.default)
                )
            elif parameter.kind == Parameter.VAR_POSITIONAL:
                positional_unlimited = True

            elif parameter.kind == Parameter.VAR_KEYWORD:
                optional_unlimited = True

            elif parameter.default is Parameter.empty:
                positional_arguments.append(parameter.name)
            else:
                optional_arguments.append((parameter.name, parameter.default))

        func.__nanohttp__ = dict(
            verbs=[verbs] if isinstance(verbs, str) else verbs,
            encoding=encoding,
            content_type=content_type,
            minimum_allowed_arguments=len(positional_arguments),
            maximum_allowed_arguments= \
                UNLIMITED if positional_unlimited else \
                len(positional_arguments) + len(optional_arguments),
            keywordonly_arguments=keywordonly_arguments,
            prevent_empty_form=prevent_empty_form,
            prevent_form=prevent_form,
            form_whitelist=form_whitelist,
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
                exstr = str(ex)
                yield f'{len(exstr)}\r\n{exstr}'
                yield '0\r\n\r\n'

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

