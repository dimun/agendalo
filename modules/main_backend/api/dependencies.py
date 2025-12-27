import sqlite3
from typing import Generator

from fastapi import Depends

from modules.main_backend.database.connection import get_db_connection
from modules.main_backend.repositories.interfaces import (
    AgendaRepository,
    AvailabilityHoursRepository,
    BusinessServiceHoursRepository,
    PersonRepository,
    RoleRepository,
)
from modules.main_backend.repositories.sqlite_repositories import (
    SQLiteAgendaRepository,
    SQLiteAvailabilityHoursRepository,
    SQLiteBusinessServiceHoursRepository,
    SQLitePersonRepository,
    SQLiteRoleRepository,
)
from modules.scheduler.interfaces import Scheduler
from modules.scheduler.or_tools_scheduler import ORToolsScheduler
from modules.main_backend.services.agenda_service import AgendaService
from modules.main_backend.services.availability_hours_service import AvailabilityHoursService
from modules.main_backend.services.business_service_hours_service import BusinessServiceHoursService
from modules.main_backend.services.calendar_service import CalendarService
from modules.main_backend.services.person_service import PersonService
from modules.main_backend.services.role_service import RoleService


def get_person_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[PersonRepository, None, None]:
    yield SQLitePersonRepository(conn)


def get_role_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[RoleRepository, None, None]:
    yield SQLiteRoleRepository(conn)


def get_availability_hours_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[AvailabilityHoursRepository, None, None]:
    yield SQLiteAvailabilityHoursRepository(conn)


def get_person_service(
    person_repo: PersonRepository = Depends(get_person_repository),
) -> PersonService:
    return PersonService(person_repo)


def get_role_service(
    role_repo: RoleRepository = Depends(get_role_repository),
) -> RoleService:
    return RoleService(role_repo)


def get_availability_hours_service(
    availability_hours_repo: AvailabilityHoursRepository = Depends(get_availability_hours_repository),
    person_repo: PersonRepository = Depends(get_person_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> AvailabilityHoursService:
    return AvailabilityHoursService(availability_hours_repo, person_repo, role_repo)


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


def get_agenda_repository(
    conn: sqlite3.Connection = Depends(get_db_connection),
) -> Generator[AgendaRepository, None, None]:
    yield SQLiteAgendaRepository(conn)


def get_scheduler() -> Scheduler:
    return ORToolsScheduler()


def get_agenda_service(
    agenda_repo: AgendaRepository = Depends(get_agenda_repository),
    availability_hours_repo: AvailabilityHoursRepository = Depends(get_availability_hours_repository),
    business_service_hours_repo: BusinessServiceHoursRepository = Depends(
        get_business_service_hours_repository
    ),
    role_repo: RoleRepository = Depends(get_role_repository),
    scheduler: Scheduler = Depends(get_scheduler),
) -> AgendaService:
    return AgendaService(
        agenda_repo,
        availability_hours_repo,
        business_service_hours_repo,
        role_repo,
        scheduler,
    )


def get_calendar_service(
    availability_hours_repo: AvailabilityHoursRepository = Depends(get_availability_hours_repository),
    person_repo: PersonRepository = Depends(get_person_repository),
    role_repo: RoleRepository = Depends(get_role_repository),
) -> CalendarService:
    return CalendarService(availability_hours_repo, person_repo, role_repo)

