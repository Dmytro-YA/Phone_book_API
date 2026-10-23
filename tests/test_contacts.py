import uuid
from dataclasses import asdict

import pytest
import requests
from faker import Faker
from config import API_BASE_URL
from exploration import payload


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


def test_add_contact_success(auth_headers, contact_data):
    contact_data_dict = asdict(contact_data)
    response = requests.post(f"{API_BASE_URL}v1/contacts", json=contact_data_dict, headers=auth_headers)
    assert response.status_code == 200
    message = response.json()
    assert "added" in message["message"].lower()

    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    contacts = list_response.json()["contacts"]
    matching_contacts = [
        contact
        for contact in contacts
        if contact["name"] == contact_data_dict["name"]
           and contact["lastName"] == contact_data_dict["lastName"]
           and contact["email"] == contact_data_dict["email"]
           and contact["phone"] == contact_data_dict["phone"]
           and contact["address"] == contact_data_dict["address"]
    ]
    try:
        assert len(matching_contacts) == 1
    finally:
        for contact in matching_contacts:
            requests.delete(f"{API_BASE_URL}v1/contacts/{contact['id']}", headers=auth_headers)

def test_add_contact_success_1(auth_headers, created_contact):
    response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    contacts = response.json()["contacts"]

    matching_contacts = [contact for contact in response.json()["contacts"] if contact["id"] ==created_contact["id"]]
    assert len(matching_contacts)==1
    assert matching_contacts[0] ==created_contact

def test_contact_full_lifecycle(auth_headers):
    new_contact = {
        "name": "Agata",
        "lastName": "Students",
        "email": f"agata@gmail.com",
        "phone": "808541506018",
        "address": "home sweet home",
        "description": "agata is living at home"
    }
    response = requests.post(f"{API_BASE_URL}v1/contacts", json=new_contact, headers=auth_headers)
    assert response.status_code == 200
    message = response.json()["message"]
    contact_id = message.split(": ")[1]

    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"]==contact_id]
    assert len(matching_contact) == 1
    assert matching_contact[0]["id"] == contact_id

    payload = dict(new_contact)
    payload["id"] = contact_id
    payload["name"] = "Agata2"

    update_response = requests.put(f"{API_BASE_URL}v1/contacts/", json=payload, headers=auth_headers)
    assert update_response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == contact_id]
    assert len(matching_contact) == 1


    delete_response = requests.delete(f"{API_BASE_URL}v1/contacts/{contact_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert contact_id not in contact_ids


def test_update_contact_phone(auth_headers, created_contact):
    new_phone = "8085415069"
    payload = dict(created_contact)
    payload["phone"] = new_phone
    update_response = requests.put(f"{API_BASE_URL}v1/contacts", json=payload, headers=auth_headers)
    assert update_response.status_code == 200
    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0]["phone"] == new_phone
    assert matching_contact[0] == payload

def test_update_contact_email(auth_headers, created_contact):
    new_email = "8085415069@gmail.com"
    payload = dict(created_contact)
    payload["email"] = new_email
    update_response = requests.put(f"{API_BASE_URL}v1/contacts", json=payload, headers=auth_headers)
    assert update_response.status_code == 200
    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0]["email"] == new_email
    assert matching_contact[0] == payload


@pytest.mark.parametrize(
    "field, new_value",
    [
        pytest.param("name", "Agata2", id="name_updated"),
        pytest.param("lastName", "Students2", id="lastName_updated"),
        pytest.param("email", f"updated_{uuid.uuid4().hex[:8]}@gmail.com", id="email_updated"),
        pytest.param("phone", "8085415069", id="phone_updated"),
        pytest.param("address", "home sweet home2", id="address_updated"),
        pytest.param("description", "agata is living at home2", id="description_updated")
    ])
def test_update_contact_field(auth_headers, created_contact, field, new_value):
    payload = dict(created_contact)
    payload[field] = new_value

    response = requests.put(f"{API_BASE_URL}v1/contacts", json=payload, headers=auth_headers)
    assert response.status_code == 200
    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    matching_contact = [c for c in list_response.json()["contacts"] if c["id"] == created_contact["id"]]
    assert len(matching_contact) == 1
    assert matching_contact[0][field] == new_value
    assert matching_contact[0] == payload


def test_delete_contact_success(auth_headers, created_contact):
    delete_response = requests.delete(f"{API_BASE_URL}v1/contacts/{created_contact['id']}", headers=auth_headers)
    assert delete_response.status_code == 200
    list_response = requests.get(f"{API_BASE_URL}v1/contacts", headers=auth_headers)
    contact_ids = [c["id"] for c in list_response.json()["contacts"]]
    assert created_contact not in contact_ids
