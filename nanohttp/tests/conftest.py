import os
import sys
import time
import tempfile
import shutil
import socket
from os import path
from multiprocessing import Process

import pytest

from nanohttp import main


@pytest.fixture
def make_temp_file():
    temp_files = []

    def _make_temp_file(**kw):
        """
        Structure example: {'a.html': 'Hello', 'b': {}}
        """
        filename = tempfile.mktemp()
        temp_files.append(filename)
        return filename

    yield _make_temp_file

    for f in temp_files:
        os.remove(f)


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
        def wrapper(self, args):
            from pytest_cov.embed import cleanup_on_sigterm
            cleanup_on_sigterm()
            sys.exit(main(args))

        def execute(self, *a):
            port = free_port
            args = ['nanohttp', f'-b{port}']
            args.extend(a)
            self.subprocess = Process(target=self.wrapper, args=(args, ))
            self.subprocess.start()
            time.sleep(.2)
            return f'http://localhost:{port}/'

        def terminate(self):
            if self.subprocess is None:
                # Already terminated
                return
            self.subprocess.terminate()
            while self.subprocess.exitcode is None:
                time.sleep(.1)
                self.subprocess.join(.3)
            self.subprocess = None

        @property
        def exitstatus(self):
            while self.subprocess.exitcode is None:
                time.sleep(.1)
                self.subprocess.join(.3)
            return self.subprocess.exitcode

    tool = Tool()
    yield tool
    tool.terminate()

