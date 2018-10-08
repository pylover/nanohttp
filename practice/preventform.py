from nanohttp import *


class Root(RestController):
    @text(prevent_form=True)
    def foo(self):
        return 'foo'


if __name__ == '__main__':
    quickstart(Root())

