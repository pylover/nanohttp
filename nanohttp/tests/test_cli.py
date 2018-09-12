
import requests


def test_cli_without_arguments(clitool):
    url = clitool.execute()
    response = requests.get(url)
    assert response.status_code == 200
    assert len(response.text) > 1
