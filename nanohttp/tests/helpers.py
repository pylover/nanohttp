import functools

import bddrest

from nanohttp import Application, configure, settings


def Given(controller_factory, *args, configuration=None, **kwargs):
    if configuration:
        configure(configuration, force=True)
    else:
        configure(force=True)

    application = Application(controller_factory)
    return bddrest.Given(application, None, *args, **kwargs)


when = functools.partial(bddrest.when, None)

