

def action(methods='any', encoding='utf8'):

    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods
        func.http_encoding = encoding
        return func

    return _decorator
