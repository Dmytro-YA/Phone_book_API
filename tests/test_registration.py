import uuid

import requests

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA


def test_registration_with_valid_data_return_token():
    payload =\
        {"username": f"user_{uuid.uuid4().hex[:8]}@gmail.com",
         "password": "Qwerty123!"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert "token" in body
    assert len(body["token"]) > 0
    assert "application/json" in response.headers["Content-Type"]


def test_registration_with_existing_user_rejected():
    payload =\
        {"username": TEST_USER_EMAIL,
         "password": TEST_USER_PASSWORD
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 409


def test_registration_with_invalid_email_rejected():
    payload =\
        {"username": "invalid_email.com",
         "password": "Qwerty123!"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400


def test_registration_with_weak_password_rejected():
    payload =\
        {"username": f"user_{uuid.uuid4().hex[:8]}@gmail.com",
         "password": "123"
         }
    response = requests.post(f"{BA}v1/user/registration/usernamepassword", json=payload)
    assert response.status_code == 400
