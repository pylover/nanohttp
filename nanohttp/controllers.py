
import time
import os
import sys
import logging
import traceback
from os.path import isdir, join, relpath, pardir, exists
from mimetypes import guess_type

import ujson

from .configuration import settings
from .exceptions import HttpStatus, InternalServerError, HttpNotFound, HttpMethodNotAllowed, HttpForbidden
from .contexts import context, Context
from .constants import HTTP_DATETIME_FORMAT


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('nanohttp')


class Controller(object):
    __logger__ = logger
    __http_methods__ = 'any'
    __response_encoding__ = 'utf8'
    __default_action__ = 'index'
    __remove_trailing_slash__ = True

    def _hook(self, name, *args, **kwargs):
        if hasattr(self, name):
            return getattr(self, name)(*args, **kwargs)

    def load_app(self):
        self._hook('app_load')
        return self._handle_request

    def _handle_exception(self, ex):
        context.response_encoding = 'utf-8'

        error = ex if isinstance(ex, HttpStatus) else InternalServerError(sys.exc_info())
        error_page = self._hook('request_error', error)
        message = error.status_text
        description = error.render() if settings.debug else error.info if error_page is None else error_page

        if context.response_content_type == 'application/json':
            response = ujson.encode(dict(
                message=message,
                description=description
            ))
        else:
            context.response_content_type = 'text/plain'
            response = "%s\n%s" % (message, description)

        if isinstance(error, InternalServerError):
            traceback.print_exc()

        def resp():
            yield response

        return error.status, resp()

    def _handle_request(self, environ, start_response):
        ctx = Context(environ)
        ctx.__enter__()
        # start_response("200 OK", [('Content-Type', 'text/plain; charset=utf-8')])

        status = '200 OK'
        buffer = None

        try:
            self._hook('begin_request')
            if self.__remove_trailing_slash__:
                ctx.path = ctx.path.rstrip('/')

            result = self(*ctx.path.split('?')[0][1:].split('/'))
            if result:
                resp_generator = iter(result)
                buffer = next(resp_generator)
            else:
                resp_generator = None

        except Exception as ex:
            self.__logger__.exception('Exception while handling the request.')
            status, resp_generator = self._handle_exception(ex)

        finally:
            self._hook('begin_response')

            if context.response_cookies:
                for cookie in context.response_cookies:
                    ctx.response_headers.add_header(*cookie.http_set_cookie())
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
                    yield str(ex_).encode()
                raise ex_

            finally:
                self._hook('end_response')
                context.__exit__(*sys.exc_info())

        return _response()

    # noinspection PyMethodMayBeStatic
    def _serve_handler(self, handler, *remaining_paths):
        if hasattr(handler, '__response_encoding__'):
            context.response_encoding = handler.__response_encoding__

        if hasattr(handler, '__content_type__'):
            context.response_content_type = handler.__content_type__

        return handler(*remaining_paths)

    def _dispatch(self, *remaining_paths):
        if not len(remaining_paths):
            path = self.__default_action__
        else:
            path = self.__default_action__ if remaining_paths[0] == '' else remaining_paths[0]
            remaining_paths = remaining_paths[1:]

        # Ensuring the handler
        handler = getattr(self, path, None)
        if handler is None:
            handler = getattr(self, self.__default_action__, None)
            if handler is not None:
                remaining_paths = (path, ) + remaining_paths

        args_count = len(remaining_paths)
        if (handler is None or not hasattr(handler, '__http_methods__')) \
                or (hasattr(handler, '__argcount__') and handler.__argcount__ < args_count) \
                or (hasattr(handler, '__annotations__') and len(handler.__annotations__) < args_count):
            raise HttpNotFound()

        if 'any' != handler.__http_methods__ and context.method not in handler.__http_methods__:
            raise HttpMethodNotAllowed()

        return handler, remaining_paths

    def __call__(self, *remaining_paths):
        handler, remaining_paths = self._dispatch(*remaining_paths)
        return self._serve_handler(handler, *remaining_paths)


class RestController(Controller):

    def _dispatch(self, *remaining_paths):
        handler = None
        if remaining_paths:
            first_path = remaining_paths[0]
            if hasattr(self, first_path):
                remaining_paths = remaining_paths[1:]
                handler = getattr(self, first_path)

        if handler is None:
            if not hasattr(self, context.method):
                raise HttpMethodNotAllowed()

            handler = getattr(self, context.method)

        if handler is None or not hasattr(handler, '__http_methods__'):
            raise HttpNotFound()

        # FIXME: check argcount
        if hasattr(handler, '__annotations__') and len(handler.__annotations__) < len(remaining_paths):
            raise HttpNotFound()

        return handler, remaining_paths


class Static(Controller):
    __response_encoding__ = None
    __chunk_size__ = 0x4000

    def __init__(self, directory='.', default_document='index.html'):
        self.default_document = default_document
        self.directory = directory

    def __call__(self, *remaining_paths):

        # Find the physical path of the given path parts
        physical_path = join(self.directory, *remaining_paths)

        # Check to do not access the parent directory of root and also we are not listing directories here.
        if pardir in relpath(physical_path, self.directory):
            raise HttpForbidden()

        if isdir(physical_path):
            if self.default_document:
                physical_path = join(physical_path, self.default_document)
                if not exists(physical_path):
                    raise HttpForbidden
            else:
                raise HttpForbidden()

        context.response_headers.add_header('Content-Type', guess_type(physical_path)[0] or 'application/octet-stream')

        try:
            f = open(physical_path, mode='rb')
            stat = os.fstat(f.fileno())
            context.response_headers.add_header('Content-Length', str(stat[6]))
            context.response_headers.add_header(
                'Last-Modified',
                time.strftime(HTTP_DATETIME_FORMAT, time.gmtime(stat.st_mtime))
            )

            with f:
                while True:
                    r = f.read(self.__chunk_size__)
                    if not r:
                        break
                    yield r

        except OSError:
            raise HttpNotFound()
