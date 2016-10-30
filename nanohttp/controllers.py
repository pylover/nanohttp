

from nanohttp import HttpStatus, context, HttpNotFound, HttpMethodNotAllowed
from nanohttp.context import Context


class Controller(object):

    def wsgi_app(self, environ, start_response):
        with Context(environ):
            # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

            status = "200 OK"

            try:
                return self(*context.path[1:].split('/'))
            except HttpStatus as ex:
                status = ex.status
            except Exception as ex:
                # FIXME: Handle exception !
                status = "500 Internal server error"
                raise ex
            finally:
                start_response(status, context.headers)

            return ''

    def __call__(self, path, *remaining_paths):

        path = path or 'index'
        func = getattr(self, path, None)
        if func is None \
                or not hasattr(func, 'http_methods') \
                or func.__code__.co_argcount != len(remaining_paths) + 1:
            raise HttpNotFound()

        if 'any' not in func.http_methods and context.method not in func.http_methods:
            raise HttpMethodNotAllowed()

        return func(*remaining_paths)



if __name__ == '__main__':
    from wsgiref.simple_server import make_server, demo_app

    httpd = make_server('', 8000, demo_app)
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()

    # # Alternative: serve one request, then exit
    # httpd.handle_request()
