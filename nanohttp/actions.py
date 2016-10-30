

def action(methods='any'):

    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods
        return func

    return _decorator
