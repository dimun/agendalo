import sqlite3
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db_connection
from app.database.connection import get_db_connection as original_get_db_connection
from app.main import app


_shared_test_conn: sqlite3.Connection | None = None


def _get_test_db_connection() -> Generator[sqlite3.Connection, None, None]:
    global _shared_test_conn
    if _shared_test_conn is None:
        _shared_test_conn = sqlite3.connect(":memory:", check_same_thread=False)
        _shared_test_conn.row_factory = sqlite3.Row
        cursor = _shared_test_conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS roles (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS availability_hours (
                id TEXT PRIMARY KEY,
                person_id TEXT NOT NULL,
                role_id TEXT NOT NULL,
                day_of_week INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                is_recurring INTEGER NOT NULL,
                specific_date TEXT,
                FOREIGN KEY(person_id) REFERENCES people(id),
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS business_service_hours (
                id TEXT PRIMARY KEY,
                role_id TEXT NOT NULL,
                day_of_week INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                start_date TEXT,
                end_date TEXT,
                is_recurring INTEGER NOT NULL,
                specific_date TEXT,
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agendas (
                id TEXT PRIMARY KEY,
                role_id TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agenda_entries (
                id TEXT PRIMARY KEY,
                agenda_id TEXT NOT NULL,
                person_id TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                role_id TEXT NOT NULL,
                FOREIGN KEY(agenda_id) REFERENCES agendas(id),
                FOREIGN KEY(person_id) REFERENCES people(id),
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agenda_coverage (
                id TEXT PRIMARY KEY,
                agenda_id TEXT NOT NULL,
                date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                role_id TEXT NOT NULL,
                is_covered INTEGER NOT NULL,
                required_person_count INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY(agenda_id) REFERENCES agendas(id),
                FOREIGN KEY(role_id) REFERENCES roles(id)
            )
        """)

        _shared_test_conn.commit()
    yield _shared_test_conn


@pytest.fixture(autouse=True)
def reset_test_db():
    global _shared_test_conn
    if _shared_test_conn:
        cursor = _shared_test_conn.cursor()
        cursor.execute("DELETE FROM agenda_entries")
        cursor.execute("DELETE FROM agenda_coverage")
        cursor.execute("DELETE FROM agendas")
        cursor.execute("DELETE FROM availability_hours")
        cursor.execute("DELETE FROM business_service_hours")
        cursor.execute("DELETE FROM people")
        cursor.execute("DELETE FROM roles")
        _shared_test_conn.commit()


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    global _shared_test_conn
    _shared_test_conn = None

    app.dependency_overrides[get_db_connection] = _get_test_db_connection

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    if _shared_test_conn:
        _shared_test_conn.close()
        _shared_test_conn = None

