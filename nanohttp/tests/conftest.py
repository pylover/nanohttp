import os
import tempfile
from os import path
import shutil

import pytest


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

