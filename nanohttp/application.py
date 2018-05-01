
import sys
import types
import logging

from nanohttp.contexts import Context, context
from nanohttp.exceptions import HttpStatus
from nanohttp.configuration import settings
from nanohttp.constants import NO_CONTENT_STATUSES


logger = logging.getLogger('nanohttp')


class Application:
    """ Application main handler """

    #: Application logger based on python builtin logging module
    __logger__ = logger

    #: The root controller
    __root__ = None

    def __init__(self, root=None):
        """
        Initialize application and calling ``app_init`` hook.

        .. note:: ``__root__`` attribute will set by ``root`` parameter.

        :param root: The root controller
        """
        self.__root__ = root
        self._hook('app_init')

    def _hook(self, name, *args, **kwargs):
        """ Call the hook

        :param name: Hook name
        :param args: Pass to the hook positional arguments
        :param kwargs: Pass to the hook keyword arguments
        """
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
        """ Method that `WSGI <https://www.python.org/dev/peps/pep-0333/#id15>`_ server calls """
        # Entering the context
        ctx = Context(environ, self)
        ctx.__enter__()

        # Preparing some variables
        status = '200 OK'
        buffer = None
        response_iterable = None

        try:
            self._hook('begin_request')

            # Removing the trailing slash in-place, if exists
            ctx.path = ctx.path.rstrip('/')

            # Removing the heading slash, and query string anyway
            path = ctx.path[1:].split('?')[0]

            # Splitting the path by slash(es) if any
            remaining_paths = path.split('/') if path else []

            # Calling the controller, actually this will be serve our request
            response_body = self.__root__(*remaining_paths)

            if response_body:
                # The goal is to yield an iterable, to encode and iter over it at the end of this method.
                if isinstance(response_body, types.GeneratorType):
                    # Generators are iterable !
                    response_iterable = response_body
                    # Trying to get at least one element from the generator, to force the method call till the second
                    # `yield` statement
                    buffer = next(response_iterable)
                elif isinstance(response_body, (str, bytes)):
                    # Mocking the body inside an iterable to prevent the iteration over the str character by character
                    # For more info check the pull-request #34, https://github.com/Carrene/nanohttp/pull/34
                    response_iterable = (response_body, )
                else:
                    # Assuming the body is an iterable.
                    response_iterable = response_body

        except Exception as ex:
            # the self._handle_exception may raise the error again, if the error is not subclass of the HttpStatus,
            # Otherwise, a tuple of the status code and response body will be returned.
            status, response_body = self._handle_exception(ex)
            buffer = None
            response_iterable = (response_body, )

        self._hook('begin_response')

        # Setting cookies in response headers, if any
        cookie = ctx.cookies.output()
        if cookie:
            for line in cookie.split('\r\n'):
                ctx.response_headers.add_header(*line.split(': ', 1))

        # Sometimes don't need to transfer any body, for example the 304 case.
        if status[:3] in NO_CONTENT_STATUSES:
            del ctx.response_headers['Content-Type']
            start_response(status, ctx.response_headers.items())
            # This is only header, and body should not be transferred.
            # So the context is also should be destroyed
            context.__exit__(*sys.exc_info())
            return []
        else:
            start_response(status, ctx.response_headers.items())

        # It seems we have to transfer a body, so this function should yield a generator of the body chunks.
        def _response():
            try:
                if buffer is not None:
                    yield ctx.encode_response(buffer)

                if response_iterable:
                    # noinspection PyTypeChecker
                    for chunk in response_iterable:
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

    def shutdown(self):
        pass
