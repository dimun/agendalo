from uuid import UUID

import pytest
from fastapi.testclient import TestClient


def test_create_role(client: TestClient):
    response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Developer"
    assert data["description"] == "Software developer"
    assert "id" in data


def test_get_all_roles(client: TestClient):
    client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    client.post(
        "/api/roles",
        json={"name": "Manager", "description": "Team manager"},
    )

    response = client.get("/api/roles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(r["name"] == "Developer" for r in data)
    assert any(r["name"] == "Manager" for r in data)


def test_get_role_by_id(client: TestClient):
    create_response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    role_id = create_response.json()["id"]

    response = client.get(f"/api/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "Developer"
    assert data["description"] == "Software developer"


def test_get_role_not_found(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/roles/{fake_id}")
    assert response.status_code == 404

