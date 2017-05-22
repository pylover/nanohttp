
import time
import os
import logging
from os.path import isdir, join, relpath, pardir, exists
from mimetypes import guess_type

from .exceptions import HttpNotFound, HttpMethodNotAllowed, HttpForbidden
from .contexts import context
from .constants import HTTP_DATETIME_FORMAT


logging.basicConfig(level=logging.INFO)


class Controller(object):
    __http_methods__ = 'any'
    __response_encoding__ = 'utf8'
    __default_action__ = 'index'
    __remove_trailing_slash__ = True

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
    __detect_verb_by_header__ = False

    def _dispatch(self, *remaining_paths):
        handler = None
        if remaining_paths:
            first_path = remaining_paths[0]
            if hasattr(self, first_path):
                remaining_paths = remaining_paths[1:]
                handler = getattr(self, first_path)

        if handler is None:

            if self.__detect_verb_by_header__ and context.environ.get(self.__detect_verb_by_header__):
                handler = getattr(self, context.environ.get(self.__detect_verb_by_header__).lower())
            elif not hasattr(self, context.method):
                raise HttpMethodNotAllowed()
            else:
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
