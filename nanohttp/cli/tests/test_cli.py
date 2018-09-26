from os import path

import requests


def test_cli_without_arguments(clitool):
    url = clitool.execute()
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


# Erorred because of the travis buf about change ditectory:
# https://github.com/pytest-dev/pytest/issues/2686
def test_cli_with_change_directory_flag(clitool):
    url = clitool.execute('-C', '/tmp')
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1


def test_cli_with_given_module_name(clitool, controller_file):
    directory, filename = path.split(controller_file())
    # Removing the module[.py] extension by filename[:-3]
    url = clitool.execute('-C', directory, filename[:-3])
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'


def test_cli_with_change_dir_and_controller_filename(clitool, controller_file):
    directory, filename = path.split(controller_file())
    url = clitool.execute('-C', directory, filename)
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'


def test_cli_with_static_controller(clitool, make_temp_directory):
    directory = make_temp_directory(a='Hello A')
    url = clitool.execute('-C', directory, ':Static')
    response = requests.get(f'{url}/a')
    assert response.status_code == 200
    assert response.text == 'Hello A'


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


def test_cli_with_given_filename(clitool, controller_file):
    url = clitool.execute(controller_file())
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'


def test_cli_with_given_filename_and_controller_name(clitool, controller_file):
    url = clitool.execute(f'{controller_file()}:Root')
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'

def test_cli_with_given_package_and_controller_name(clitool, controller_file):
    directory, filename = path.split(controller_file('__init__.py'))
    url = clitool.execute(f'{directory}:Root')
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'

