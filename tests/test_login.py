from dataclasses import asdict

import pytest
import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA
from exploration import response
from tests.conftest import new_user


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

@pytest.mark.parametrize(
    "username, password",
    [
        pytest.param(TEST_USER_EMAIL, "wrongpass", id="wrong_pass_without_uppercase"),
        pytest.param(TEST_USER_EMAIL, "", id="empty_password"),
        pytest.param("wrong_email", TEST_USER_PASSWORD, id="username_not_email"),
        pytest.param("", "ghedfg!Qs", id="empty_username"),
    ]
)
def test_login_with_invalid_credentials_rejected(username, password):
    from models.user import User
    payload = asdict(User(username=username, password=password))
    response = requests.post(f"{BA}v1/user/login/usernamepassword", json=payload)
    assert response.status_code == 401

def test_login_unknown_user_rejected(new_user):

    payload = asdict(new_user)
    response = requests.post(f"{BA}v1/user/login/usernamepassword", json=payload)
    assert response.status_code == 401
    assert "password" in response.json()["message"].lower()

