import sqlite3
from datetime import date, datetime, time
from uuid import UUID, uuid4

from app.domain.models import (
    Agenda,
    AgendaCoverage,
    AgendaEntry,
    AvailabilityHours,
    BusinessServiceHours,
    Person,
    Role,
)
from app.repositories.interfaces import (
    AgendaRepository,
    AvailabilityHoursRepository,
    BusinessServiceHoursRepository,
    PersonRepository,
    RoleRepository,
)


class SQLitePersonRepository(PersonRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create(self, person: Person) -> Person:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO people (id, name, email) VALUES (?, ?, ?)",
            (str(person.id), person.name, person.email),
        )
        self.conn.commit()
        return person

    def get_by_id(self, person_id: UUID) -> Person | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM people WHERE id = ?", (str(person_id),))
        row = cursor.fetchone()
        if row:
            return Person(
                id=UUID(row["id"]),
                name=row["name"],
                email=row["email"],
            )
        return None

    def get_all(self) -> list[Person]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM people")
        rows = cursor.fetchall()
        return [
            Person(
                id=UUID(row["id"]),
                name=row["name"],
                email=row["email"],
            )
            for row in rows
        ]

    def update(self, person: Person) -> Person:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE people SET name = ?, email = ? WHERE id = ?",
            (person.name, person.email, str(person.id)),
        )
        self.conn.commit()
        return person

    def delete(self, person_id: UUID) -> bool:
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM people WHERE id = ?", (str(person_id),))
        self.conn.commit()
        return cursor.rowcount > 0


class SQLiteRoleRepository(RoleRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create(self, role: Role) -> Role:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO roles (id, name, description) VALUES (?, ?, ?)",
            (str(role.id), role.name, role.description),
        )
        self.conn.commit()
        return role

    def get_by_id(self, role_id: UUID) -> Role | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM roles WHERE id = ?", (str(role_id),))
        row = cursor.fetchone()
        if row:
            return Role(
                id=UUID(row["id"]),
                name=row["name"],
                description=row["description"],
            )
        return None

    def get_all(self) -> list[Role]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM roles")
        rows = cursor.fetchall()
        return [
            Role(
                id=UUID(row["id"]),
                name=row["name"],
                description=row["description"],
            )
            for row in rows
        ]


class SQLiteAvailabilityHoursRepository(AvailabilityHoursRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create(self, availability_hours: AvailabilityHours) -> AvailabilityHours:
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO availability_hours 
               (id, person_id, role_id, day_of_week, start_time, end_time, 
                start_date, end_date, is_recurring, specific_date) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(availability_hours.id),
                str(availability_hours.person_id),
                str(availability_hours.role_id),
                availability_hours.day_of_week,
                availability_hours.start_time.isoformat(),
                availability_hours.end_time.isoformat(),
                availability_hours.start_date.isoformat() if availability_hours.start_date else None,
                availability_hours.end_date.isoformat() if availability_hours.end_date else None,
                1 if availability_hours.is_recurring else 0,
                availability_hours.specific_date.isoformat() if availability_hours.specific_date else None,
            ),
        )
        self.conn.commit()
        return availability_hours

    def get_by_person(self, person_id: UUID) -> list[AvailabilityHours]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM availability_hours WHERE person_id = ?",
            (str(person_id),),
        )
        rows = cursor.fetchall()
        return [self._row_to_availability_hours(row) for row in rows]

    def get_by_role(self, role_id: UUID) -> list[AvailabilityHours]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM availability_hours WHERE role_id = ?",
            (str(role_id),),
        )
        rows = cursor.fetchall()
        return [self._row_to_availability_hours(row) for row in rows]

    def get_by_date_range(self, start_date: date, end_date: date) -> list[AvailabilityHours]:
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM availability_hours 
               WHERE (is_recurring = 1 AND day_of_week IS NOT NULL)
               OR (specific_date IS NOT NULL AND specific_date >= ? AND specific_date <= ?)
               OR (start_date IS NOT NULL AND end_date IS NOT NULL 
                   AND start_date <= ? AND end_date >= ?)""",
            (
                start_date.isoformat(),
                end_date.isoformat(),
                end_date.isoformat(),
                start_date.isoformat(),
            ),
        )
        rows = cursor.fetchall()
        return [self._row_to_availability_hours(row) for row in rows]

    def delete(self, availability_hours_id: UUID) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM availability_hours WHERE id = ?",
            (str(availability_hours_id),),
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def _row_to_availability_hours(self, row: sqlite3.Row) -> AvailabilityHours:
        return AvailabilityHours(
            id=UUID(row["id"]),
            person_id=UUID(row["person_id"]),
            role_id=UUID(row["role_id"]),
            day_of_week=row["day_of_week"],
            start_time=time.fromisoformat(row["start_time"]),
            end_time=time.fromisoformat(row["end_time"]),
            start_date=date.fromisoformat(row["start_date"]) if row["start_date"] else None,
            end_date=date.fromisoformat(row["end_date"]) if row["end_date"] else None,
            is_recurring=bool(row["is_recurring"]),
            specific_date=date.fromisoformat(row["specific_date"]) if row["specific_date"] else None,
        )


class SQLiteBusinessServiceHoursRepository(BusinessServiceHoursRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create(self, business_service_hours: BusinessServiceHours) -> BusinessServiceHours:
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO business_service_hours 
               (id, role_id, day_of_week, start_time, end_time, 
                start_date, end_date, is_recurring, specific_date) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(business_service_hours.id),
                str(business_service_hours.role_id),
                business_service_hours.day_of_week,
                business_service_hours.start_time.isoformat(),
                business_service_hours.end_time.isoformat(),
                business_service_hours.start_date.isoformat() if business_service_hours.start_date else None,
                business_service_hours.end_date.isoformat() if business_service_hours.end_date else None,
                1 if business_service_hours.is_recurring else 0,
                business_service_hours.specific_date.isoformat() if business_service_hours.specific_date else None,
            ),
        )
        self.conn.commit()
        return business_service_hours

    def get_by_role(self, role_id: UUID) -> list[BusinessServiceHours]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM business_service_hours WHERE role_id = ?",
            (str(role_id),),
        )
        rows = cursor.fetchall()
        return [self._row_to_business_service_hours(row) for row in rows]

    def get_by_date_range(self, start_date: date, end_date: date) -> list[BusinessServiceHours]:
        cursor = self.conn.cursor()
        cursor.execute(
            """SELECT * FROM business_service_hours 
               WHERE (is_recurring = 1 AND day_of_week IS NOT NULL)
               OR (specific_date IS NOT NULL AND specific_date >= ? AND specific_date <= ?)
               OR (start_date IS NOT NULL AND end_date IS NOT NULL 
                   AND start_date <= ? AND end_date >= ?)""",
            (
                start_date.isoformat(),
                end_date.isoformat(),
                end_date.isoformat(),
                start_date.isoformat(),
            ),
        )
        rows = cursor.fetchall()
        return [self._row_to_business_service_hours(row) for row in rows]

    def get_all(self) -> list[BusinessServiceHours]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM business_service_hours")
        rows = cursor.fetchall()
        return [self._row_to_business_service_hours(row) for row in rows]

    def get_by_id(self, business_service_hours_id: UUID) -> BusinessServiceHours | None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM business_service_hours WHERE id = ?",
            (str(business_service_hours_id),),
        )
        row = cursor.fetchone()
        if row:
            return self._row_to_business_service_hours(row)
        return None

    def delete(self, business_service_hours_id: UUID) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM business_service_hours WHERE id = ?",
            (str(business_service_hours_id),),
        )
        self.conn.commit()
        return cursor.rowcount > 0

    def _row_to_business_service_hours(self, row: sqlite3.Row) -> BusinessServiceHours:
        return BusinessServiceHours(
            id=UUID(row["id"]),
            role_id=UUID(row["role_id"]),
            day_of_week=row["day_of_week"],
            start_time=time.fromisoformat(row["start_time"]),
            end_time=time.fromisoformat(row["end_time"]),
            start_date=date.fromisoformat(row["start_date"]) if row["start_date"] else None,
            end_date=date.fromisoformat(row["end_date"]) if row["end_date"] else None,
            is_recurring=bool(row["is_recurring"]),
            specific_date=date.fromisoformat(row["specific_date"]) if row["specific_date"] else None,
        )


class SQLiteAgendaRepository(AgendaRepository):
    def __init__(self, connection: sqlite3.Connection):
        self.conn = connection

    def create(self, agenda: Agenda) -> Agenda:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO agendas (id, role_id, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (
                str(agenda.id),
                str(agenda.role_id),
                agenda.status,
                agenda.created_at.isoformat(),
                agenda.updated_at.isoformat(),
            ),
        )
        self.conn.commit()
        return agenda

    def get_by_id(self, agenda_id: UUID) -> Agenda | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agendas WHERE id = ?", (str(agenda_id),))
        row = cursor.fetchone()
        if row:
            return Agenda(
                id=UUID(row["id"]),
                role_id=UUID(row["role_id"]),
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
        return None

    def get_by_role(self, role_id: UUID) -> list[Agenda]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agendas WHERE role_id = ?", (str(role_id),))
        rows = cursor.fetchall()
        return [
            Agenda(
                id=UUID(row["id"]),
                role_id=UUID(row["role_id"]),
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def get_by_role_and_status(self, role_id: UUID, status: str) -> list[Agenda]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM agendas WHERE role_id = ? AND status = ?",
            (str(role_id), status),
        )
        rows = cursor.fetchall()
        return [
            Agenda(
                id=UUID(row["id"]),
                role_id=UUID(row["role_id"]),
                status=row["status"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
            )
            for row in rows
        ]

    def create_entry(self, entry: AgendaEntry) -> AgendaEntry:
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO agenda_entries 
               (id, agenda_id, person_id, date, start_time, end_time, role_id) 
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                str(entry.id),
                str(entry.agenda_id),
                str(entry.person_id),
                entry.date.isoformat(),
                entry.start_time.isoformat(),
                entry.end_time.isoformat(),
                str(entry.role_id),
            ),
        )
        self.conn.commit()
        return entry

    def get_entries_by_agenda(self, agenda_id: UUID) -> list[AgendaEntry]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM agenda_entries WHERE agenda_id = ?", (str(agenda_id),)
        )
        rows = cursor.fetchall()
        return [
            AgendaEntry(
                id=UUID(row["id"]),
                agenda_id=UUID(row["agenda_id"]),
                person_id=UUID(row["person_id"]),
                date=date.fromisoformat(row["date"]),
                start_time=time.fromisoformat(row["start_time"]),
                end_time=time.fromisoformat(row["end_time"]),
                role_id=UUID(row["role_id"]),
            )
            for row in rows
        ]

    def create_coverage(self, coverage: AgendaCoverage) -> AgendaCoverage:
        cursor = self.conn.cursor()
        cursor.execute(
            """INSERT INTO agenda_coverage 
               (id, agenda_id, date, start_time, end_time, role_id, is_covered, required_person_count) 
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                str(coverage.id),
                str(coverage.agenda_id),
                coverage.date.isoformat(),
                coverage.start_time.isoformat(),
                coverage.end_time.isoformat(),
                str(coverage.role_id),
                1 if coverage.is_covered else 0,
                coverage.required_person_count,
            ),
        )
        self.conn.commit()
        return coverage

    def get_coverage_by_agenda(self, agenda_id: UUID) -> list[AgendaCoverage]:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM agenda_coverage WHERE agenda_id = ?", (str(agenda_id),)
        )
        rows = cursor.fetchall()
        return [
            AgendaCoverage(
                id=UUID(row["id"]),
                agenda_id=UUID(row["agenda_id"]),
                date=date.fromisoformat(row["date"]),
                start_time=time.fromisoformat(row["start_time"]),
                end_time=time.fromisoformat(row["end_time"]),
                role_id=UUID(row["role_id"]),
                is_covered=bool(row["is_covered"]),
                required_person_count=row["required_person_count"],
            )
            for row in rows
        ]

    def update_status(self, agenda_id: UUID, status: str) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE agendas SET status = ?, updated_at = ? WHERE id = ?",
            (status, datetime.now().isoformat(), str(agenda_id)),
        )
        self.conn.commit()
        return cursor.rowcount > 0

