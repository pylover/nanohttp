import os
import sys
import time
import shutil
import socket
import signal
import tempfile
from os import path
from multiprocessing import Process

import pytest
from pytest_cov.embed import cleanup

from nanohttp import main, quickstart, settings


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

        def terminate_subprocess(self, sig, frame):  # pragma: no cover
            cleanup()
            sys.exit(sig)

        def wrapper(self, args):
            signal.signal(signal.SIGTERM, self.terminate_subprocess)
            sys.exit(main(args))

        def execute(self, *a):
            port = free_port
            args = ['nanohttp', f'-b{port}']
            args.extend(a)
            self.subprocess = Process(
                target=self.wrapper,
                args=(args, ),
                daemon=True
            )
            self.subprocess.start()
            time.sleep(.5)
            return f'http://localhost:{port}'

        def _wait_for(self):
            if self.subprocess.is_alive():
                self.subprocess.terminate()
            self.subprocess.join()

        def terminate(self):
            if self.subprocess is not None:
                self._wait_for()
                self.subprocess = None

        @property
        def exitstatus(self):
            self._wait_for()
            return self.subprocess.exitcode

    tool = Tool()
    yield tool
    tool.terminate()


@pytest.fixture
def controller_file(make_temp_directory):
    def _create(name='foo.py'):
        directory = make_temp_directory()
        filename = path.join(directory, name)
        with open(filename, 'w') as f:
            f.write(
                'from nanohttp import Controller, action\n'
                'class Root(Controller):\n'
                '    @action\n'
                '    def index(self):\n'
                '        yield \'Index\'\n'
            )
        return filename
    yield _create


@pytest.fixture
def run_quickstart(free_port):
    terminators = []
    settings.__class__._instance = None
    def wrapper(*args, **kw):
        terminate = quickstart(*args, block=False, port=free_port, **kw)
        time.sleep(.1)
        terminators.append(terminate)
        return f'http://localhost:{free_port}'
    yield wrapper
    for t in terminators:
        t()
        time.sleep(.1)


