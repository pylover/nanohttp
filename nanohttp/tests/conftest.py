import functools

import pytest
import bddrest

from nanohttp import Application


@pytest.fixture(scope='session')
def given():

    import pudb; pudb.set_trace()  # XXX BREAKPOINT
    @functools.wraps(bddrest.Given)
    def wrapper(controller_factory, *args, **kwargs):
        application = Application(controller_factory)
        return bddrest.Given(application, None, *args, **kwargs)

    yield wrapper

