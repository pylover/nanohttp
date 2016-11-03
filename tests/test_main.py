
import time
import unittest
import threading
from os.path import join, dirname

import httplib2

from nanohttp import main
from tests.helpers import find_free_tcp_port


class EntryPointTestCase(unittest.TestCase):

    def setUp(self):
        self.demo_filename = join(dirname(__file__), 'stuff/demo.txt')
        with open(self.demo_filename, mode='w') as f:
            f.write('some text')
        self.port = find_free_tcp_port()
        self.url = 'http://localhost:%s/tests/stuff/demo.txt' % self.port

    def test_main_function(self):

        args = ['nanohttp', '-d', '.', '-b', str(self.port), 'nanohttp:Static']
        t = threading.Thread(target=main, args=(args,), daemon=True)
        t.start()

        time.sleep(.5)

        client = httplib2.Http()
        response, content = client.request(self.url)
        self.assertEqual(response.status, 200)
        self.assertEqual(content, b'some text')
