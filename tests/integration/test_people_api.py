from uuid import UUID

import pytest
from fastapi.testclient import TestClient


def test_create_person(client: TestClient):
    response = client.post(
        "/api/people",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data


def test_get_all_people(client: TestClient):
    client.post(
        "/api/people",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    client.post(
        "/api/people",
        json={"name": "Jane Smith", "email": "jane@example.com"},
    )

    response = client.get("/api/people")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(p["name"] == "John Doe" for p in data)
    assert any(p["name"] == "Jane Smith" for p in data)


def test_get_person_by_id(client: TestClient):
    create_response = client.post(
        "/api/people",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    person_id = create_response.json()["id"]

    response = client.get(f"/api/people/{person_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == person_id
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"


def test_get_person_not_found(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/people/{fake_id}")
    assert response.status_code == 404

