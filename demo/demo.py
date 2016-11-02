
from os.path import dirname, abspath
from nanohttp import Controller, html, context, Static, HttpFound, settings


class Root(Controller):
    static = Static(abspath(dirname(__file__)))

    @html
    def index(self):
        yield '<html><head><title>nanohttp demo</title></head><body>'
        yield '<h1>nanohttp demo page</h1>'
        yield '<h2>debug flag is: %s</h2>' % settings.debug
        yield '<img src="/static/cat.jpg" />'
        yield '<ul>'
        yield from ('<li><b>%s:</b> %s</li>' % i for i in context.environ.items())
        yield '</ul>'
        yield '</body>'

    @html(methods=['post', 'put'])
    def contact(self):
        yield '<h1>Thanks: %s</h1>' % context.form['name'] if context.form else 'Please send a name.'

    @html
    def google(self):
        raise HttpFound('http://google.com')

    @html
    def error(self):
        raise Exception()


if __name__ == '__main__':
    from nanohttp import quickstart
    quickstart(Root())
