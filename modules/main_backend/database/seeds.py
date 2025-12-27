import sqlite3
from uuid import UUID, uuid5

from modules.main_backend.config import settings
from modules.main_backend.domain.models import Person, Role

NAMESPACE_SEED = UUID("6ba7b810-9dad-11d1-80b4-00c04fd430c8")


def _uuid_from_string(seed: str) -> UUID:
    return uuid5(NAMESPACE_SEED, seed)


def seed_database() -> None:
    conn = sqlite3.connect(settings.get_database_path(), check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM people")
    people_count = cursor.fetchone()[0]

    if people_count == 0:
        seed_people = [
            Person(id=_uuid_from_string("1"), name="John Doe", email="john@example.com"),
            Person(id=_uuid_from_string("2"), name="Jane Smith", email="jane@example.com"),
            Person(id=_uuid_from_string("3"), name="Bob Johnson", email="bob@example.com"),
        ]

        for person in seed_people:
            cursor.execute(
                "INSERT INTO people (id, name, email) VALUES (?, ?, ?)",
                (str(person.id), person.name, person.email),
            )

    cursor.execute("SELECT COUNT(*) FROM roles")
    roles_count = cursor.fetchone()[0]

    if roles_count == 0:
        seed_roles = [
            Role(id=_uuid_from_string("1"), name="Doctor", description="Medical doctor"),
            Role(id=_uuid_from_string("2"), name="Nurse", description="Registered nurse"),
            Role(id=_uuid_from_string("3"), name="Receptionist", description="Front desk staff"),
        ]

        for role in seed_roles:
            cursor.execute(
                "INSERT INTO roles (id, name, description) VALUES (?, ?, ?)",
                (str(role.id), role.name, role.description),
            )

    conn.commit()
    conn.close()

