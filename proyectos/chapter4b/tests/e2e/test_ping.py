import pytest
import requests

import config




@pytest.mark.usefixtures('restart_api')
def test_ping():
    url = config.get_api_url()
    r = requests.post(
        f'{url}/ping'
    )
    assert r.status_code == 200
