import pytest

from nanohttp import int_or_notfound, HTTPNotFound


def test_int_or_notfound():
    assert int_or_notfound(1) == 1
    assert int_or_notfound('1') == 1
    assert int_or_notfound(1.2) == 1
    assert int_or_notfound('-1') == -1
    assert int_or_notfound(-1) == -1
    assert int_or_notfound(False) == 0
    assert int_or_notfound(True) == 1

    with pytest.raises(HTTPNotFound):
        int_or_notfound('not integer')

    with pytest.raises(HTTPNotFound):
        int_or_notfound([1, 2])

    with pytest.raises(HTTPNotFound):
        int_or_notfound('1.2')

    with pytest.raises(HTTPNotFound):
        int_or_notfound('')

    with pytest.raises(HTTPNotFound):
        int_or_notfound(None)

    with pytest.raises(HTTPNotFound):
        int_or_notfound('1.0')

