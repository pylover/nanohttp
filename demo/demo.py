
from os.path import dirname, abspath
from nanohttp import Controller, action, context, Static


class Root(Controller):
    static = Static(abspath(dirname(__file__)))

    @action()
    def index(self):
        yield from ('%s: %s\n' % i for i in context.environ.items())

    @action(content_type='text/html')
    def cat(self):
        yield '<img src="/static/cat.jpg" />'


if __name__ == '__main__':
    from nanohttp import quickstart
    quickstart(Root())
