
import threading
import time
import unittest
from os.path import join, dirname, abspath

import httplib2

from nanohttp import main
from nanohttp.tests.helpers import find_free_tcp_port


class EntryPointTestCase(unittest.TestCase):

    def setUp(self):
        this_dir = abspath(dirname(__file__))
        self.demo_filename = join(this_dir, 'stuff/demo.txt')
        self.module_dir = abspath(join(this_dir, '..'))
        with open(self.demo_filename, mode='w') as f:
            f.write('some text')
        self.port = find_free_tcp_port()
        self.url = 'http://localhost:%s/tests/stuff/demo.txt' % self.port

    def test_main_function(self):

        args = ['nanohttp', '-C', self.module_dir, '-b', str(self.port), ':Static']
        t = threading.Thread(target=main, args=(args,), daemon=True)
        t.start()

        time.sleep(1)

        client = httplib2.Http()
        response, content = client.request(self.url)
        self.assertIsNotNone(response)
        self.assertIsNotNone(content)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
