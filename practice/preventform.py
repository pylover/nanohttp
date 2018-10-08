from nanohttp import *


class Root(RestController):
    @text(prevent_form=True)
    def abc(self):
        return 'default'

