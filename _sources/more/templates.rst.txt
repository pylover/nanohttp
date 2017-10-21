Templates
=========

nanohttp have no any plan to officially support template engines.
But you can implement any template engines (like
`Mako <http://www.makotemplates.org/>`_,
`Jinja <http://jinja.pocoo.org/>`_,
`Mustache <https://github.com/defunkt/pystache>`_, etc.).

This is how to use `Mako <http://www.makotemplates.org/>`_ template engine with the nanohttp:

``main.py``

..  code-block:: python

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

``templates/index.html``

..  code-block:: html+mako

    <html>
    <head>
        <title>nanohttp mako example</title>
    </head>
    <body>
        <h1>WSGI environ</h1>
        <ul>
        %for key, value in environ.items():
          <li><b>${key}:</b> ${value}</li>
        %endfor
        </ul>
    </body>
    </html>

