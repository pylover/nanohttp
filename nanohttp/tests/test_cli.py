import time

import pytest
import requests


def test_cli_without_arguments(clitool):
    url = clitool.execute()
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


def test_cli_with_change_directory_flag(clitool):
    url = clitool.execute('-C', '/tmp')
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


def test_cli_with_config_file_flag(clitool, make_temp_file):
    filename = make_temp_file()
    with open(filename, 'w') as f:
        f.write('debug: false')

    url = clitool.execute('-c', filename)
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


def test_cli_with_option_flag(clitool):
    url = clitool.execute('-o', 'debug=false', '-o', 'foo=bar')
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


def test_cli_with_invalid_option_flag(clitool):
    url = clitool.execute('-o', 'a.b=1' )
    assert clitool.exitstatus != 0


