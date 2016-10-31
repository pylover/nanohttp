

def action(methods='any', encoding='utf8', content_type='text/plain'):

    def _decorator(func):
        func.http_methods = methods.split(',') if isinstance(methods, str) else methods
        
        if encoding.replace('-', '').lower() != 'utf8':
            func.http_encoding = encoding

        if content_type:
            func.content_type = content_type

        return func

    return _decorator
