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
def free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind((socket.gethostname(), 0))
        return s.getsockname()[1]
    finally:
        s.close()


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

