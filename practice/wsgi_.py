

def app(environ, start_response):
    raise Exception()
    start_response('200 OK', [('Content-Type', 'text/plain')])
    yield b'Hello World\n'
