import sqlite3
from typing import Generator

from fastapi import Depends

from app.database.connection import get_db_connection
from app.repositories.interfaces import (
    BusinessServiceHoursRepository,
    PersonRepository,
    RoleRepository,
    WorkingHoursRepository,
)
from app.repositories.sqlite_repositories import (
    SQLiteBusinessServiceHoursRepository,
    SQLitePersonRepository,
    SQLiteRoleRepository,
    SQLiteWorkingHoursRepository,
)
from app.services.business_service_hours_service import BusinessServiceHoursService
from app.services.calendar_service import CalendarService
from app.services.person_service import PersonService
from app.services.role_service import RoleService
from app.services.working_hours_service import WorkingHoursService


def get_person_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[PersonRepository, None, None]:
    yield SQLitePersonRepository(conn)


def get_role_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[RoleRepository, None, None]:
    yield SQLiteRoleRepository(conn)


def get_working_hours_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[WorkingHoursRepository, None, None]:
    yield SQLiteWorkingHoursRepository(conn)


def get_person_service(
    person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)


def get_role_service(
    role_repo: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    return RoleService(role_repo)


def get_working_hours_service(
    working_hours_repo: WorkingHoursRepository = Depends(get_working_hours_repository),
    person_repo: PersonRepository = Depends(get_person_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> WorkingHoursService:
    return WorkingHoursService(working_hours_repo, person_repo, role_repo)


def get_business_service_hours_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[BusinessServiceHoursRepository, None, None]:
    yield SQLiteBusinessServiceHoursRepository(conn)


def get_business_service_hours_service(
    business_service_hours_repo: BusinessServiceHoursRepository = Depends(
        get_business_service_hours_repository
    ),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> BusinessServiceHoursService:
    return BusinessServiceHoursService(business_service_hours_repo, role_repo)


def get_calendar_service(
    working_hours_repo: WorkingHoursRepository = Depends(get_working_hours_repository),
    person_repo: PersonRepository = Depends(get_person_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> CalendarService:
    return CalendarService(working_hours_repo, person_repo, role_repo)

