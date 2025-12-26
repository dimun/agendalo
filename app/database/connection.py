import sqlite3
from typing import Generator

from app.config import settings


def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    conn = sqlite3.connect(settings.get_database_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database() -> None:
    conn = sqlite3.connect(settings.get_database_path())
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

