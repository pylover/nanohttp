import functools

import bddrest

from nanohttp import Application, configure, settings


def Given(controller, *args, configuration=None, **kwargs):
    if configuration:
        configure(configuration, force=True)
    else:
        configure(force=True)

    if isinstance(controller, Application):
        application = controller
    else:
        application = Application(controller)
    return bddrest.Given(application, None, *args, **kwargs)


when = functools.partial(bddrest.when, None)

