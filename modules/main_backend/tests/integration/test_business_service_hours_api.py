from datetime import date

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def role_id(client: TestClient) -> str:
    response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    return response.json()["id"]


def test_create_business_service_hours_recurring(client: TestClient, role_id: str):
    response = client.post(
        "/api/business-service-hours",
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
    assert data["role_id"] == role_id
    assert data["day_of_week"] == 0
    assert data["start_time"] == "09:00:00"
    assert data["end_time"] == "17:00:00"
    assert data["is_recurring"] is True


def test_create_business_service_hours_specific_date(client: TestClient, role_id: str):
    response = client.post(
        "/api/business-service-hours",
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
    assert data["role_id"] == role_id
    assert data["specific_date"] == "2024-01-15"
    assert data["is_recurring"] is False


def test_get_all_business_service_hours(client: TestClient, role_id: str):
    client.post(
        "/api/business-service-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get("/api/business-service-hours")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role_id"] == role_id


def test_get_business_service_hours_by_role(client: TestClient, role_id: str):
    client.post(
        "/api/business-service-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get(f"/api/business-service-hours?role_id={role_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role_id"] == role_id


def test_get_business_service_hours_by_date_range(client: TestClient, role_id: str):
    client.post(
        "/api/business-service-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get(
        "/api/business-service-hours?start_date=2024-01-01&end_date=2024-01-31"
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_business_service_hours_by_id(client: TestClient, role_id: str):
    create_response = client.post(
        "/api/business-service-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    business_service_hours_id = create_response.json()["id"]

    response = client.get(f"/api/business-service-hours/{business_service_hours_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == business_service_hours_id
    assert data["role_id"] == role_id


def test_get_business_service_hours_not_found(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/business-service-hours/{fake_id}")
    assert response.status_code == 404


def test_delete_business_service_hours(client: TestClient, role_id: str):
    create_response = client.post(
        "/api/business-service-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    business_service_hours_id = create_response.json()["id"]

    response = client.delete(f"/api/business-service-hours/{business_service_hours_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/business-service-hours/{business_service_hours_id}")
    assert get_response.status_code == 404


def test_delete_business_service_hours_not_found(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.delete(f"/api/business-service-hours/{fake_id}")
    assert response.status_code == 404


def test_create_business_service_hours_role_not_found(client: TestClient):
    fake_role_id = "00000000-0000-0000-0000-000000000000"
    response = client.post(
        "/api/business-service-hours",
        json={
            "role_id": fake_role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )
    assert response.status_code == 404

