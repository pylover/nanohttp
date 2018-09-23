
import time
import os
import re
import logging
from os.path import isdir, join, relpath, pardir, exists
from mimetypes import guess_type

from .exceptions import HTTPNotFound, HTTPMethodNotAllowed, HTTPForbidden, \
    HTTPStatus
from .contexts import context
from .constants import HTTP_DATETIME_FORMAT, UNLIMITED


logging.basicConfig(level=logging.INFO)



class Controller(object):
    """Base Controller
    """

    __nanohttp__ = dict(
        verbs=['any'],
        encoding='utf8',
        default_action='index',
        minimum_allowed_arguments=0,
        maximum_allowed_arguments=UNLIMITED
    )

    def _get_default_handler(self, remaining_paths):
        default_action = self.__nanohttp__['default_action']
        handler = getattr(self, default_action, None)
        if not handler:
            raise HTTPNotFound()

        return handler, remaining_paths

    def _find_handler(self, remaining_paths):
        if not remaining_paths or not hasattr(self, remaining_paths[0]):
            # Handler is not found, trying default handler
            return self._get_default_handler(remaining_paths)

        return getattr(self, remaining_paths[0], None), remaining_paths[1:]

    def _validate_handler(self, handler, remaining_paths):
        if not callable(handler) or not hasattr(handler, '__nanohttp__'):
            raise HTTPNotFound()

        manifest = handler.__nanohttp__
        min_arguments = manifest.get('minimum_allowed_arguments')
        max_arguments = manifest.get('maximum_allowed_arguments')
        args_len = len(remaining_paths)
        verbs = manifest.get('verbs', 'any')

        if min_arguments > args_len or \
                (max_arguments != UNLIMITED and max_arguments < args_len):
            raise HTTPNotFound()

        if verbs != ['any'] and context.method not in verbs:
            raise HTTPMethodNotAllowed()

        prevent_empty_form = manifest.get('prevent_empty_form')
        if prevent_empty_form and len(context.form) <= 0:
            raise HTTPStatus(
                prevent_empty_form \
                if isinstance(prevent_empty_form, str) \
                else '400 Empty Form'
            )

        prevent_form = manifest.get('prevent_form')
        if prevent_form and len(context.form) > 0:
            raise HTTPStatus(
                prevent_form \
                if isinstance(prevent_form, str) \
                else '400 Form Not Allowed'
            )

        form_whitelist = manifest.get('form_whitelist')
        if form_whitelist:
            if isinstance(form_whitelist, tuple):
                form_whitelist, status = form_whitelist
            else:
                status = None

            for k in context.form:
                if k not in form_whitelist:
                    raise HTTPStatus(
                        status or f'400 Field: {k} Not Allowed'
                    )

        return handler, remaining_paths

    def _serve_handler(self, handler, remaining_paths):
        context.response_encoding = handler.__nanohttp__.get('encoding', None)
        context.response_content_type = \
            handler.__nanohttp__.get('content_type', None)

        kwargs = {}
        for k, v in handler.__nanohttp__.get('keywordonly_arguments', []):
            value = context.query.get(k)
            if value:
                kwargs[k] = value

        return handler(*remaining_paths, **kwargs)

    def __call__(self, *remaining_paths):
        handler, remaining_paths = self._find_handler(list(remaining_paths))
        handler, remaining_paths = \
            self._validate_handler(handler, remaining_paths)
        return self._serve_handler(handler, remaining_paths)


class RestController(Controller):
    """HTTP method oriented controller
    """
    def _find_handler(self, remaining_paths):
        if remaining_paths and hasattr(self, remaining_paths[0]):
            return getattr(self, remaining_paths[0], None), remaining_paths[1:]

        # Handler is not found, trying verb
        if not hasattr(self, context.method):
            raise HTTPMethodNotAllowed()

        return getattr(self, context.method), remaining_paths


class Static(Controller):
    """Serves static files
    """
    __nanohttp__ = dict(
        verbs=['any'],
        encoding=None,
        default_action='index',
        minimum_allowed_arguments=0,
        maximum_allowed_arguments=UNLIMITED
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

        # Check to do not access the parent directory of root and also we are
        # not listing directories here.
        if pardir in relpath(physical_path, self.directory):
            raise HTTPForbidden()

        if isdir(physical_path):
            if not self.default_document:
                raise HTTPNotFound()

            physical_path = join(physical_path, self.default_document)
            if not (self.default_document and exists(physical_path)):
                raise HTTPNotFound()

        context.response_headers.add_header(
            'Content-Type',
            guess_type(physical_path)[0] or 'application/octet-stream'
        )

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
            raise HTTPNotFound()


class RegexRouteController(Controller):
    """This is how to use it:

    .. code-block:: python

       class Root(RegexRouteController):

           def __init__(self):
               super().__init__((
                   (r'/installations/(?P<installation_id>\\d+)/access_tokens',
                   self.access_tokens),
               ))

           @json
           def access_tokens(self, installation_id: int):
               return dict(installationId=installation_id)

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
        raise HTTPNotFound()
