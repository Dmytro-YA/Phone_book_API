import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA
from exploration import response


def test_login_with_valid_credentials_return_token():
    payload =\
        {"username": TEST_USER_EMAIL,
         "password": TEST_USER_PASSWORD
         }
    response = requests.post(f"{BA}v1/user/login/usernamepassword", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert len(body["token"]) > 0
    assert "application/json" in response.headers["Content-Type"]