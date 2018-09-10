import sys


def app(environ, start_response):
    try:
        raise Exception()
    except:
        import pudb; pudb.set_trace()  # XXX BREAKPOINT
        start_response(
            '200 OK', [('Content-Type', 'text/plain')],
            exc_info=sys.exc_info()
        )
    #import pudb; pudb.set_trace()  # XXX BREAKPOINT
    #yield b'Hello World\n'
