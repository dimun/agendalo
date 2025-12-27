from datetime import date, time

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def person_id(client: TestClient) -> str:
    response = client.post(
        "/api/people",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    return response.json()["id"]


@pytest.fixture
def role_id(client: TestClient) -> str:
    response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    return response.json()["id"]


def test_create_availability_hours_recurring(client: TestClient, person_id: str, role_id: str):
    response = client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["person_id"] == person_id
    assert data["role_id"] == role_id
    assert data["day_of_week"] == 0
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "17:00:00"
    assert data["is_recurring"] is True


def test_create_availability_hours_specific_date(
    client: TestClient, person_id: str, role_id: str
):
    response = client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": role_id,
            "start_time": "10:00:00",
            "end_time": "18:00:00",
            "is_recurring": False,
            "specific_date": "2024-01-15",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["person_id"] == person_id
    assert data["role_id"] == role_id
    assert data["specific_date"] == "2024-01-15"
    assert data["is_recurring"] is False


def test_get_availability_hours_by_person(client: TestClient, person_id: str, role_id: str):
    client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get(f"/api/people/{person_id}/availability-hours")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["person_id"] == person_id
    assert data[0]["role_id"] == role_id


def test_get_availability_hours_by_role(client: TestClient, person_id: str, role_id: str):
    client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get(f"/api/availability-hours?role_id={role_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role_id"] == role_id


def test_get_availability_hours_by_date_range(
    client: TestClient, person_id: str, role_id: str
):
    client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get(
        "/api/availability-hours?start_date=2024-01-01&end_date=2024-01-31"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_create_availability_hours_person_not_found(client: TestClient, role_id: str):
    fake_person_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/api/people/{fake_person_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    assert response.status_code == 404


def test_create_availability_hours_role_not_found(client: TestClient, person_id: str):
    fake_role_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        f"/api/people/{person_id}/availability-hours",
        json={
            "role_id": fake_role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    assert response.status_code == 404

