
from nanohttp import Controller, text


class Root(Controller):
    @text
    def index(self):
        yield 'Hello World!'
