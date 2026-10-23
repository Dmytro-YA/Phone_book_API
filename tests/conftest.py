import uuid
from dataclasses import asdict

import pytest
import requests
from faker import Faker

from config import TEST_USER_EMAIL, TEST_USER_PASSWORD, API_BASE_URL as BA
from models.contact import Contact
from models.user import User

fake = Faker()
@pytest.fixture(scope="session")
def auth_token():
    payload = {
        "username": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    response = requests.post(f"{BA}v1/user/login/usernamepassword", json=payload)
    assert response.status_code == 200
    token = response.json()["token"]
    return token

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def unique_email():
    return f"user_{uuid.uuid4().hex[:8]}@gmail.com"

@pytest.fixture
def new_user(unique_email):
    return User(username= unique_email, password= "Qwerty123!")

@pytest.fixture
def contact_data():
    return Contact(
        name=fake.first_name(),
        lastName=fake.last_name(),
        email=fake.email(),
        phone=fake.numerify("05##########"),
        address=fake.address(),
        description="autotes"
    )

@pytest.fixture
def created_contact(auth_headers, contact_data):
    response = requests.post(f"{BA}v1/contacts", json=asdict(contact_data), headers=auth_headers)
    assert response.status_code == 200
    message = response.json()["message"]
    contact_id = message.split(": ")[1]
    created = asdict(contact_data)
    created["id"] = contact_id
    yield created
    list_response = requests.get(f"{BA}v1/contacts", headers=auth_headers)
    existing_ids = [contact["id"] for contact in list_response.json()["contacts"]]
    if contact_id in existing_ids:
        delete_response = requests.delete(f"{BA}v1/contacts/{contact_id}", headers=auth_headers)
        assert delete_response.status_code == 200