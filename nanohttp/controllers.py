

from nanohttp import HttpStatus, context, HttpNotFound, HttpMethodNotAllowed, InternalServerError
from nanohttp.context import Context


class Controller(object):

    def _hook(self, name):
        if hasattr(self, name):
            return getattr(self, name)()

    def load_app(self):
        self._hook('app_load')
        return self.handle_request

    def handle_request(self, environ, start_response):
        with Context(environ):
            # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

            status = '200 OK'
            buffer = None

            try:
                self._hook('begin_request')
                # for chunk in self(*context.path[1:].split('/')):
                #     yield chunk
                resp_generator = iter(self(*context.path[1:].split('/')))
                buffer = next(resp_generator)

            except HttpStatus as ex:
                status = ex.status
                resp_generator = iter(ex.render())

            except Exception as ex:
                # FIXME: Handle exception !
                # Giving a chance to get better output on error.
                error_page = self._hook('request_error', ex)
                e = InternalServerError(ex)
                status = e.status
                resp_generator = iter(e.render() if error_page is None else error_page)

            finally:
                start_response(status, context.headers.items())
                self._hook('start_response')

            def result():
                if buffer is not None:
                    yield buffer

                yield from resp_generator

            try:
                return result()
            finally:
                self._hook('end_request')


    def __call__(self, path, *remaining_paths):
        """
        Dispatcher
        :param path:
        :param remaining_paths:
        :return:
        """
        path = path or 'index'
        func = getattr(self, path, None)
        if func is None \
                or not hasattr(func, 'http_methods') \
                or func.__code__.co_argcount != len(remaining_paths) + 1:
            raise HttpNotFound()

        if 'any' not in func.http_methods and context.method not in func.http_methods:
            raise HttpMethodNotAllowed()

        for chunk in func(*remaining_paths):
            yield chunk.encode(func.http_encoding)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server, demo_app

    httpd = make_server('', 8000, demo_app)
    print("Serving HTTP on port 8000...")

    # Respond to requests until process is killed
    httpd.serve_forever()

    # # Alternative: serve one request, then exit
    # httpd.handle_request()
