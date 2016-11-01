
from nanohttp import Controller, action, context


class Root(Controller):

    @action()
    def index(self):
        yield from ('%s: %s\n' % i for i in context.environ.items())
