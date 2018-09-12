import os
import time
import tempfile
import shutil
import socket
from os import path
from multiprocessing import Process

import pytest

from nanohttp import main


@pytest.fixture
def make_temp_directory():
    temp_directories = []

    def create_nodes(root, **kw):
        for k, v in kw.items():
            name = path.join(root, k)

            if isinstance(v, dict):
                os.mkdir(name)
                create_nodes(name, **v)
                continue

            with open(name, 'w') as f:
                f.write(v)


    def _make_temp_directory(**kw):
        """
        Structure example: {'a.html': 'Hello', 'b': {}}
        """
        root = tempfile.mkdtemp()
        temp_directories.append(root)
        create_nodes(root, **kw)
        return root

    yield _make_temp_directory

    for d in temp_directories:
        shutil.rmtree(d)


@pytest.fixture
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket.gethostname(), 0))
        return s.getsockname()[1]
    finally:
        s.close()


@pytest.fixture
def clitool(free_port):
    class Tool:
        subprocess = None
        def execute(self, *a):
            port = free_port
            args = ['nanohttp', f'-b{port}']
            args.extend(a)
            self.subprocess = Process(target=main, args=(args, ))
            self.subprocess.start()
            time.sleep(.5)
            return f'http://localhost:{port}/'

        def terminate(self):
            self.subprocess.terminate()
            self.subprocess.join(1)
            if self.subprocess.exitcode is None:
                self.subprocess.kill()

    tool = Tool()
    yield tool
    tool.terminate()


