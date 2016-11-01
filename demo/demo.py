
from os.path import dirname, abspath
from nanohttp import Controller, html, context, Static


class Root(Controller):
    static = Static(abspath(dirname(__file__)))

    @html
    def index(self):
        yield '<img src="/static/cat.jpg" />'
        yield '<ul>'
        yield from ('<li><b>%s:</b> %s</li>' % i for i in context.environ.items())
        yield '</ul>'

    @html(methods=['post', 'put'])
    def contact(self):
        yield '<h1>Thanks: %s</h1>' % context.form['name']


if __name__ == '__main__':
    from nanohttp import quickstart
    quickstart(Root())
