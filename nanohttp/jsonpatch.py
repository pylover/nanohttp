import types
from urllib.parse import parse_qs

from . import context, action, Controller


def split_path(url):
    if '?' in url:
        path, query = url.split('?')

    else:
        path, query = url, ''

    return path, {k: v[0] if len(v) == 1 else v for k, v in parse_qs(
        query,
        keep_blank_values=True,
        strict_parsing=False
    ).items()}


class JsonPatchControllerMixin:

    def _handle_single_request(self, patch):
        context.form = patch.get('value', {})
        path, context.query = split_path(patch['path'])
        context.method = patch['op'].lower()
        remaining_paths = path.split('/')

        if remaining_paths and not remaining_paths[0]:
            return_data = self()

        else:
            return_data = self(*remaining_paths)

        if isinstance(return_data, types.GeneratorType):
            return ('"%s"' % ''.join(list(return_data)))

        else:
            return return_data

    @action(content_type='application/json')
    def patch(self: Controller):
        """
        Set context.method
        Set context.form
        :return:
        """
        # Preserve patches
        patches = context.form
        results = []
        context.jsonpatch = True

        for patch in patches:
            results.append(self._handle_single_request(patch))
            context.query = {}

        if isinstance(results, str):
            return '[%s]' % ',\n'.join(results)

        return results

