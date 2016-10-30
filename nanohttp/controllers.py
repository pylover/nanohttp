

from nanohttp import HttpStatus
from nanohttp.context import Context


class Controller(object):

    def __call__(self, path):
        return ''


class Application(Controller):

    # noinspection PyMethodOverriding
    def __call__(self, environ, start_response):
        with Context(environ) as context:
            # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

            status = "200 OK"

            try:
                return super(Application, self).__call__(context.path)
            except HttpStatus as ex:
                status = ex.status
            except Exception as ex:
                # FIXME: Handle exception !
                status = "500 Internal server error"
            finally:
                start_response(status, context.headers)

            return ''


if __name__ == '__main__':
    from wsgiref.simple_server import make_server, demo_app

    httpd = make_server('', 8000, demo_app)
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()

    # # Alternative: serve one request, then exit
    # httpd.handle_request()
