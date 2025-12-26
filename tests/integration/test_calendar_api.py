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
def role_id(client: TestClient) -> str:
    response = client.post(
        "/api/roles",
        json={"name": "Developer", "description": "Software developer"},
    )
    return response.json()["id"]


def test_get_calendar_week(client: TestClient, person_id: str, role_id: str):
    client.post(
        f"/api/people/{person_id}/working-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    response = client.get(f"/api/calendar/week?week={week_number}&year=2024")
    assert response.status_code == 200
    data = response.json()
    assert data["week"] == week_number
    assert data["year"] == 2024
    assert isinstance(data["entries"], list)


def test_get_calendar_month(client: TestClient, person_id: str, role_id: str):
    client.post(
        f"/api/people/{person_id}/working-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    response = client.get("/api/calendar/month?month=1&year=2024")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 1
    assert data["year"] == 2024
    assert isinstance(data["entries"], list)


def test_get_calendar_month_with_specific_date(
    client: TestClient, person_id: str, role_id: str
):
    client.post(
        f"/api/people/{person_id}/working-hours",
        json={
            "role_id": role_id,
            "start_time": "10:00:00",
            "end_time": "18:00:00",
            "is_recurring": False,
            "specific_date": "2024-01-15",
        },
    )

    response = client.get("/api/calendar/month?month=1&year=2024")
    assert response.status_code == 200
    data = response.json()
    assert data["month"] == 1
    assert data["year"] == 2024
    assert len(data["entries"]) >= 1
    assert any(
        entry["date"] == "2024-01-15" and entry["person_id"] == person_id
        for entry in data["entries"]
    )


def test_get_calendar_week_multiple_people(client: TestClient, role_id: str):
    person1_response = client.post(
        "/api/people",
        json={"name": "John Doe", "email": "john@example.com"},
    )
    person1_id = person1_response.json()["id"]

    person2_response = client.post(
        "/api/people",
        json={"name": "Jane Smith", "email": "jane@example.com"},
    )
    person2_id = person2_response.json()["id"]

    client.post(
        f"/api/people/{person1_id}/working-hours",
        json={
            "role_id": role_id,
            "day_of_week": 0,
            "start_time": "09:00:00",
            "end_time": "17:00:00",
            "is_recurring": True,
        },
    )

    client.post(
        f"/api/people/{person2_id}/working-hours",
        json={
            "role_id": role_id,
            "day_of_week": 1,
            "start_time": "10:00:00",
            "end_time": "18:00:00",
            "is_recurring": True,
        },
    )

    jan1_2024 = date(2024, 1, 1)
    jan1_weekday = jan1_2024.weekday()
    days_to_monday = (jan1_weekday - 0) % 7
    first_monday = jan1_2024 - timedelta(days=days_to_monday)
    if first_monday.year < 2024:
        first_monday = first_monday + timedelta(weeks=1)
    week_number = ((first_monday - date(2024, 1, 1)).days // 7) + 1

    response = client.get(f"/api/calendar/week?week={week_number}&year=2024")
    assert response.status_code == 200
    data = response.json()
    assert len(data["entries"]) >= 2
    person_ids = {entry["person_id"] for entry in data["entries"]}
    assert person1_id in person_ids
    assert person2_id in person_ids

