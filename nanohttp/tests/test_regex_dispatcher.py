
import unittest
import re

from nanohttp import text, RegexDispatchController
from nanohttp.tests.helpers import WsgiAppTestCase


class DispatcherTestCase(WsgiAppTestCase):

    class Root(RegexDispatchController):

        def __init__(self):
            super().__init__((
                (re.compile('/installations/(?P<installation_id>\d+)/access_tokens'), self.access_tokens),
            ))

        @text
        def access_tokens(self, installation_id: int):
            yield str(installation_id)

    def test_dispatch(self):
        self.assert_get('/installations/1/access_tokens', expected_response='1')
        self.assert_get('/installations/badId/access_tokens', status=404)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
