
import sys
import traceback

from nanohttp import HttpStatus, context, HttpNotFound, HttpMethodNotAllowed, InternalServerError
from nanohttp.context import Context


class Controller(object):
    http_methods = 'any'
    http_encoding = 'utf8'
    default_action = 'index'

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def load_app(self):
        self._hook('app_load')
        return self._handle_request

    def _handle_request(self, environ, start_response):
        ctx = Context(environ)
        ctx.__enter__()
        # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

        status = '200 OK'
        buffer = None

        try:
            self._hook('begin_request')
            # for chunk in self(*context.path[1:].split('/')):
            #     yield chunk
            resp_generator = iter(self(*ctx.path[1:].split('/')))
            buffer = next(resp_generator)

        except HttpStatus as ex:
            status = ex.status
            resp_generator = iter(ex.render())

        except Exception as ex:
            # FIXME: Handle exception !
            # Giving a chance to get better output on error.
            error_page = self._hook('request_error', ex)
            e = InternalServerError(sys.exc_info())
            status = e.status
            resp_generator = iter(e.render() if error_page is None else error_page)
            traceback.print_exc()

        finally:
            start_response(status, ctx.headers.items())
            self._hook('start_response')

        def _response():
            try:
                if buffer is not None:
                    yield buffer.encode(ctx.response_encoding)

                for chunk in resp_generator:
                    yield chunk.encode(ctx.response_encoding)

            finally:
                self._hook('end_request')
                context.__exit__(*sys.exc_info())

        return _response()


    def __call__(self, *remaining_paths):
        """
        Dispatcher
        :param path:
        :param remaining_paths:
        :return:
        """

        if not len(remaining_paths):
            path = self.default_action
        else:
            path = self.default_action if remaining_paths[0] == '' else remaining_paths[0]
            remaining_paths = remaining_paths[1:]

        handler = getattr(self, path, None)
        if handler is None \
                or not hasattr(handler, 'http_methods') \
                or (hasattr(handler, '__code__') and handler.__code__.co_argcount - 1 != len(remaining_paths)):
            raise HttpNotFound()

        if 'any' not in handler.http_methods and context.method not in handler.http_methods:
            raise HttpMethodNotAllowed()

        if hasattr(handler, 'http_encoding'):
            context.response_encoding = handler.http_encoding

        if hasattr(handler, 'content_type'):
            context.response_content_type = handler.content_type

        return handler(*remaining_paths)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server, demo_app

    httpd = make_server('', 8000, demo_app)
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()

    # # Alternative: serve one request, then exit
    # httpd._handle_request()
