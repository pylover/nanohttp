import threading
import time
import unittest
from os import path

import httplib2

from nanohttp import main, settings
from nanohttp.tests.helpers import find_free_tcp_port


here = path.abspath(path.dirname(__file__))


class EntryPointTestCase(unittest.TestCase):

    def setUp(self):
        self.demo_filename = path.join(here, 'stuff/demo.txt')
        self.module_dir = path.abspath(path.join(here, '..'))
        with open(self.demo_filename, mode='w') as f:
            f.write('some text')
        self.port = find_free_tcp_port()
        self.url = f'http://localhost:{self.port}/tests/stuff/demo.txt'

    def test_main_function(self):
        args = [
            'nanohttp',
            f'-C', self.module_dir,
            f'-b', str(self.port),
            ':Static',
        ]

        t = threading.Thread(target=main, args=(args,), daemon=True)
        t.start()

        time.sleep(1)

        client = httplib2.Http()
        response, content = client.request(self.url)
        self.assertIsNotNone(response)
        self.assertIsNotNone(content)

    def test_configuration_file(self):

        filename = path.join(here, 'stuff/sample.yml')

        args = [

            'nanohttp',
            f'-C', self.module_dir,
            f'--bind', str(self.port),
            f'--config-file', filename,
            ':Static',

        ]
        t = threading.Thread(target=main, args=(args,), daemon=True)
        t.start()

        time.sleep(.2)
        self.assertEqual('value', settings.custom_key)


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
