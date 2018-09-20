
import requests

from nanohttp import Application, Controller, action


def test_quickstart_without_arguments(run_quickstart):
    url = run_quickstart()
    response = requests.get(url)
    assert response.status_code == 200


def test_quickstart_with_initial_config(run_quickstart):
    url = run_quickstart(config='debug: false')
    response = requests.get(url)
    assert response.status_code == 200


def test_quickstart_with_application(run_quickstart):
    class Root(Controller):
        @action
        def index(self):
            yield f'Index'

    url = run_quickstart(application=Application(Root()))
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'


def test_quickstart_with_controller(run_quickstart):
    class Root(Controller):
        @action
        def index(self):
            yield f'Index'

    url = run_quickstart(Root())
    response = requests.get(url)
    assert response.status_code == 200
    assert response.text == 'Index'

