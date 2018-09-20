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

from nanohttp import main
from ...tests.conftest import free_port, make_temp_directory


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
def clitool(free_port):
    class Tool:
        subprocess = None
        url = None

        def terminate_subprocess(self, sig, frame):  # pragma: no cover
            cleanup()
            sys.exit(sig)

        def wrapper(self, args):
            signal.signal(signal.SIGTERM, self.terminate_subprocess)
            exitcode = main(args)
            sys.exit(exitcode)

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
            time.sleep(8 if os.environ.get('TRAVIS') else .33)
            return f'http://localhost:{port}'

        def _wait_for(self):
            if self.subprocess.is_alive():
                self.subprocess.terminate()
            self.subprocess.join(8 if os.environ.get('TRAVIS') else None)

        def terminate(self):
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

