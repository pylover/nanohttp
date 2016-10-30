
from functools import wraps

from nanohttp import request, HttpMethodNotAllowed


def action(methods='any'):
    methods = methods.split(',') if isinstance(methods, str) else methods

    def _decorator(func):

        @wraps(func)
        def _action_wrapper(controller, *args, **kwargs):
            if request.method not in methods:
                raise HttpMethodNotAllowed()

            return func(controller, *args, **kwargs)

        return _action_wrapper

    return _decorator
