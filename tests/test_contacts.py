import uuid

import pytest
import requests

from config import API_BASE_URL


def test_get_contact_without_token_rejected():
    response = requests.get(f"{API_BASE_URL}v1/contacts")
    assert response.status_code == 403


def test_get_contact_with_valid_token_accepted(auth_headers):
    response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    assert response.status_code == 200
    body = response.json()
    assert "contacts" in body
    assert isinstance(body["contacts"], list)

@pytest.mark.parametrize("authorization",
                         [
                         pytest.param("Bearer asd123", id="garbage_token"),
                         pytest.param("Bearer ", id="empty token"),
                         pytest.param("Basic asd123", id="wrong_scheme")
                         ]
                         )
def test_get_contact_with_malformed_token_rejected(authorization):
    response = requests.get(f"{API_BASE_URL}v1/contacts", headers={"Authorization": authorization})
    assert response.status_code == 401


def test_add_contact_success(auth_headers):
    new_contact = {
        "name": "Agata",
        "lastName": "Students",
        "email": f"agata_{uuid.uuid4().hex[:8]}@gmail.com",
        "phone": "808541506018",
        "address": "home sweet home",
        "description": "agata is living at home"
    }
    response = requests.post(f"{API_BASE_URL}v1/contacts", json=new_contact, headers=auth_headers)
    assert response.status_code == 200
    message = response.json()
    assert "added" in message["message"].lower()

    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    contacts = list_response.json()["contacts"]
    matching_contacts = [
        contact
        for contact in contacts
        if contact["name"] == new_contact["name"]
           and contact["lastName"] == new_contact["lastName"]
           and contact["email"] == new_contact["email"]
           and contact["phone"] == new_contact["phone"]
           and contact["address"] == new_contact["address"]
    ]
    try:
        assert len(matching_contacts) == 1
    finally:
        for contact in matching_contacts:
            requests.delete(f"{API_BASE_URL}v1/contacts/{contact['id']}", headers=auth_headers)
