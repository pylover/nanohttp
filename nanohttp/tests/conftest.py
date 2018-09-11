import functools

import pytest
import bddrest

from nanohttp import Application, configure, settings


@pytest.fixture(scope='session')
def given():

    @functools.wraps(bddrest.Given)
    def wrapper(controller_factory, *args, **kwargs):
        configure(force=True)
        application = Application(controller_factory)
        return bddrest.Given(application, None, *args, **kwargs)

    yield wrapper


@pytest.fixture(scope='session')
def when():
    return functools.partial(bddrest.when, None)

