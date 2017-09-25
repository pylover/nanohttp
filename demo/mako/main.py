
import functools
from os.path import dirname, abspath, join

from mako.lookup import TemplateLookup

from nanohttp import Controller, context, Static, settings, action


here = abspath(dirname(__file__))
lookup = TemplateLookup(directories=[join(here, 'templates')])


def render_template(func, template_name):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        result = func(*args, **kwargs)
        if hasattr(result, 'to_dict'):
            result = result.to_dict()
        elif not isinstance(result, dict):
            raise ValueError('The result must be an instance of dict, not: %s' % type(result))

        template_ = lookup.get_template(template_name)
        return template_.render(**result)

    return wrapper


template = functools.partial(action, content_type='text/html', inner_decorator=render_template)


class Root(Controller):
    static = Static(here)

    @template('index.mak')
    def index(self):
        return dict(
            settings=settings,
            environ=context.environ
        )


if __name__ == '__main__':
    from nanohttp import quickstart
    quickstart(Root(), config='')
