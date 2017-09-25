
from nanohttp import Controller, html, settings, context


class Root(Controller):

    @html
    def index(self):  # pragma: no cover
        yield '<html><head><title>nanohttp demo</title></head><body>'
        yield '<h1>nanohttp demo page</h1>'
        yield '<h2>debug flag is: %s</h2>' % settings.debug
        yield '<img src="/static/cat.jpg" />'
        yield '<ul>'
        yield from ('<li><b>%s:</b> %s</li>' % i for i in context.environ.items())
        yield '</ul>'
        yield '</body></html>'
