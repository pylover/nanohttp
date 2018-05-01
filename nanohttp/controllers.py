
import time
import os
import re
import logging
from os.path import isdir, join, relpath, pardir, exists
from mimetypes import guess_type

from .exceptions import HttpNotFound, HttpMethodNotAllowed, HttpForbidden
from .contexts import context
from .constants import HTTP_DATETIME_FORMAT


logging.basicConfig(level=logging.INFO)

UNLIMITED = -1


class Controller(object):
    """ Base Controller """

    __nanohttp__ = dict(
        verbs='any',
        encoding='utf8',
        default_action='index'
    )

    def _get_default_handler(self, remaining_paths):
        default_action = self.__nanohttp__['default_action']
        handler = getattr(self, default_action, None)
        if not handler:
            raise HttpNotFound()

        return handler, remaining_paths

    def _find_handler(self, remaining_paths):
        if not remaining_paths or not hasattr(self, remaining_paths[0]):
            # Handler is not found, trying default handler
            return self._get_default_handler(remaining_paths)

        return getattr(self, remaining_paths[0], None), remaining_paths[1:]

    # noinspection PyMethodMayBeStatic
    def _validate_handler(self, handler, remaining_paths):
        if not callable(handler) or not hasattr(handler, '__nanohttp__'):
            raise HttpNotFound()

        # noinspection PyUnresolvedReferences
        manifest = handler.__nanohttp__

        positionals = manifest.get('positional_arguments', None)
        positionals_length = len(positionals) if positionals is not None else UNLIMITED

        optionals = manifest.get('optional_arguments', None)
        optionals_length = len(optionals) if optionals is not None else UNLIMITED

        available_arguments = len(remaining_paths)
        verbs = manifest.get('verbs', 'any')

        if UNLIMITED not in (optionals_length, positionals_length) and \
                (positionals_length > available_arguments or available_arguments > (positionals_length + optionals_length)):
            raise HttpNotFound()

        if verbs is not 'any' and context.method not in verbs:
            raise HttpMethodNotAllowed()

        return handler, remaining_paths

    # noinspection PyMethodMayBeStatic
    def _serve_handler(self, handler, remaining_paths):
        context.response_encoding = handler.__nanohttp__.get('encoding', None)
        context.response_content_type = handler.__nanohttp__.get('content_type', None)

        kwargs = {}
        for k, v in handler.__nanohttp__.get('keywordonly_arguments', []):
            value = context.query_string.get(k)
            if value:
                kwargs[k] = value

        return handler(*remaining_paths, **kwargs)

    def __call__(self, *remaining_paths):
        handler, remaining_paths = self._find_handler(list(remaining_paths))
        handler, remaining_paths = self._validate_handler(handler, remaining_paths)
        return self._serve_handler(handler, remaining_paths)


class RestController(Controller):
    """
    HTTP method oriented controller
    """
    def _find_handler(self, remaining_paths):
        if remaining_paths and hasattr(self, remaining_paths[0]):
            return getattr(self, remaining_paths[0], None), remaining_paths[1:]

        # Handler is not found, trying verb
        if not hasattr(self, context.method):
            raise HttpMethodNotAllowed()

        return getattr(self, context.method), remaining_paths


class Static(Controller):
    """
    Serves static files
    """
    __nanohttp__ = dict(
        verbs='any',
        encoding=None,
        default_action='index'
    )

    __chunk_size__ = 0x4000

    def __init__(self, directory='.', default_document='index.html'):
        """
        :param directory: Directory path to server
        :param default_document: Default document to serve as index
        """
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


class RegexRouteController(Controller):
    """
    This is how to use it:

    .. code-block:: python

        class Root(RegexRouteController):

            def __init__(self):
                super().__init__((
                    ('/installations/(?P<installation_id>\d+)/access_tokens', self.access_tokens),
                ))

            @json
            def access_tokens(self, installation_id: int):
                return dict(
                    installationId=installation_id
                )


    """

    def __init__(self, routes):
        """
        :param routes: Routes list in (regex, method) format
        """
        self.routes = [(re.compile(p), a) for p, a in routes]

    def _find_handler(self, remaining_paths):
        path = '/' + '/'.join(remaining_paths)
        for pattern, handler in self.routes:
            match = pattern.match(path)
            if match:
                return handler, match.groups()
        raise HttpNotFound()
