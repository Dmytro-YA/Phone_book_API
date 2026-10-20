import uuid
from dataclasses import asdict

import pytest
import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA


from models.user import User
from tests.conftest import new_user


def test_registration_with_valid_data_return_token(new_user):
    # payload =\
    #     {"username": unique_email,
    #      "password": "Qwerty123!"
    #      }
    # user = User(
    #     username=unique_email,
    #     password="Qwerty123!"
    # )
    payload = asdict(new_user)

    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert len(body["token"]) > 0
    assert "application/json" in response.headers["Content-Type"]


def test_registration_with_empty_email_rejected():
    # payload =\
    #     {"username": "",
    #      "password": "Qwerty123!"
    #      }
    user = User(
        username="",
        password="Qwerty123!"
    )
    payload = asdict(user)
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400


def test_registration_with_existing_user_rejected(new_user):
    payload = asdict(new_user)
    first_response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert first_response.status_code == 200
    second_response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert second_response.status_code == 409
    assert "already exists" in second_response.json()["message"]


def test_registration_with_invalid_email_rejected():
    payload =\
        {"username": "invalid_email.com",
         "password": "Qwerty123!"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "username" in response.json()["message"]
    body = response.json()
    assert body["status"] ==400
    assert body["error"]=="Bad Request"
    assert body["path"]=="/v1/user/registration/usernamepassword"

def test_registration_password_without_uppercase_rejected(unique_email):
    payload = \
        {"username": unique_email,
         "password": "qwerty123!"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "password" in response.json()["message"]


def test_registration_password_toshort_rejected(unique_email):
    payload = \
        {"username": unique_email,
         "password": "Qty3!"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert "password" in response.json()["message"]

def test_registration_with_weak_password_rejected(unique_email):
    payload =\
        {"username": unique_email,
         "password": "123"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400

@pytest.mark.parametrize(
     "field,bad_value",
    [
      pytest.param("password","Pass12$", id="password_too_short"),
      pytest.param("password","password123$", id="password_no_uppercase"),
      pytest.param("password","PASSWORD123$", id="password_no_lowercase"),
      pytest.param("password","PASSWORD$", id="password_no_digits"),
      pytest.param("password","Password123", id="password_no_special_char"),
      pytest.param("username","user@", id="username_no_domain"),
      pytest.param("username","notanemail", id="username_no_at_sign"),
      pytest.param("username","@gmail.com", id="username_no_local_part"),
    ]

)
def test_registration_with_invalid_value_rejected(new_user, field, bad_value):
    payload = asdict(new_user)
    payload[field] = bad_value
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert field in response.json()["message"]
    assert "token" not in response.json()

@pytest.mark.parametrize("missing_field", ["username", "password"])

def test_registration_missing_field_rejected(new_user, missing_field):
    payload = asdict(new_user)
    del payload[missing_field]
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
    assert missing_field in response.json()["message"]
    assert "token" not in response.json()



