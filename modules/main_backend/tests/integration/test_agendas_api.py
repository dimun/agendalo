from datetime import date, timedelta

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
def person2_id(client: TestClient) -> str:
    response = client.post(
        "/api/people",
        json={"name": "Jane Smith", "email": "jane@example.com"},
    )
    return response.json()["id"]


@pytest.fixture
def role_id(client: TestClient) -> str:
    response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    return response.json()["id"]


@pytest.fixture
def setup_availability_and_business_hours(
    client: TestClient, person_id: str, person2_id: str, role_id: str
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

    client.post(
        f"/api/people/{person2_id}/availability-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

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


def test_generate_agenda_maximize_coverage(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    response = client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "maximize_coverage",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["role_id"] == role_id
    assert "entries" in data
    assert "coverage" in data
    assert len(data["entries"]) > 0


def test_generate_agenda_minimize_gaps(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    response = client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "minimize_gaps",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["role_id"] == role_id
    assert "entries" in data
    assert "coverage" in data


def test_generate_agenda_balance_workload(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    response = client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "balance_workload",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "draft"
    assert data["role_id"] == role_id
    assert "entries" in data
    assert "coverage" in data


def test_generate_agenda_invalid_strategy(client: TestClient, role_id: str):
    response = client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [1],
            "year": 2024,
            "optimization_strategy": "invalid_strategy",
        },
    )

    assert response.status_code == 400


def test_get_agenda(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    create_response = client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "maximize_coverage",
        },
    )
    agenda_id = create_response.json()["id"]

    response = client.get(f"/api/agendas/{agenda_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agenda_id
    assert data["role_id"] == role_id
    assert "entries" in data
    assert "coverage" in data


def test_get_agenda_not_found(client: TestClient):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/agendas/{fake_id}")
    assert response.status_code == 404


def test_get_agendas_by_role(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "maximize_coverage",
        },
    )

    response = client.get(f"/api/agendas?role_id={role_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(agenda["role_id"] == role_id for agenda in data)


def test_get_agendas_by_role_and_status(
    client: TestClient,
    role_id: str,
    setup_availability_and_business_hours,
):
    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    client.post(
        "/api/agendas/generate",
        json={
            "role_id": role_id,
            "weeks": [week_number],
            "year": 2024,
            "optimization_strategy": "maximize_coverage",
        },
    )

    response = client.get(f"/api/agendas?role_id={role_id}&status=draft")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(agenda["status"] == "draft" for agenda in data)

