
import sys
import logging

from nanohttp.contexts import Context, context
from nanohttp.exceptions import HttpStatus
from nanohttp.configuration import settings


logger = logging.getLogger('nanohttp')


class Application:
    __logger__ = logger
    __root__ = None

    def __init__(self, root=None):
        self.__root__ = root
        self._hook('app_init')

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def _handle_exception(self, ex):
        """This method should return a tuple of (status, resp_generator) and or raise the exception.

        :param ex: The exception to examine
        :return: status, resp_generator
        """
        if isinstance(ex, HttpStatus):
            return ex.status, ex.render()

        self.__logger__.exception('Internal Server Error', exc_info=True)
        self._hook('end_response')
        context.__exit__(*sys.exc_info())
        raise ex

    def __call__(self, environ, start_response):
        ctx = Context(environ, self)
        ctx.__enter__()
        # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

        status = '200 OK'
        buffer = None

        try:
            self._hook('begin_request')
            if self.__root__.__remove_trailing_slash__:
                ctx.path = ctx.path.rstrip('/')

            result = self.__root__(*ctx.path.split('?')[0][1:].split('/'))
            if result:
                resp_generator = iter(result)
                buffer = next(resp_generator)
            else:
                resp_generator = None

        except Exception as ex:
            status, resp_generator = self._handle_exception(ex)

        self._hook('begin_response')

        # Setting cookies in response headers
        cookie = ctx.cookies.output()
        if cookie:
            for line in cookie.split('\r\n'):
                ctx.response_headers.add_header(*line.split(': ', 1))

        start_response(status, ctx.response_headers.items())

        def _response():
            try:
                if buffer is not None:
                    yield ctx.encode_response(buffer)

                if resp_generator:
                    # noinspection PyTypeChecker
                    for chunk in resp_generator:
                        yield ctx.encode_response(chunk)
                else:
                    yield b''
            except Exception as ex_:  # pragma: no cover
                self.__logger__.exception('Exception while serving the response.')
                if settings.debug:
                    # FIXME: Proper way to handle exceptions after start_response
                    yield str(ex_).encode()
                raise ex_

            finally:
                self._hook('end_response')
                context.__exit__(*sys.exc_info())

        return _response()
