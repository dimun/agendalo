from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from modules.main_backend.domain.models import (
    Agenda,
    AgendaCoverage,
    AgendaEntry,
    AvailabilityHours,
    BusinessServiceHours,
    Person,
    Role,
)


class PersonRepository(ABC):
    @abstractmethod
    def create(self, person: Person) -> Person:
        pass

    @abstractmethod
    def get_by_id(self, person_id: UUID) -> Person | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Person]:
        pass

    @abstractmethod
    def update(self, person: Person) -> Person:
        pass

    @abstractmethod
    def delete(self, person_id: UUID) -> bool:
        pass


class RoleRepository(ABC):
    @abstractmethod
    def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    def get_by_id(self, role_id: UUID) -> Role | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Role]:
        pass


class AvailabilityHoursRepository(ABC):
    @abstractmethod
    def create(self, availability_hours: AvailabilityHours) -> AvailabilityHours:
        pass

    @abstractmethod
    def get_by_person(self, person_id: UUID) -> list[AvailabilityHours]:
        pass

    @abstractmethod
    def get_by_role(self, role_id: UUID) -> list[AvailabilityHours]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> list[AvailabilityHours]:
        pass

    @abstractmethod
    def delete(self, availability_hours_id: UUID) -> bool:
        pass


class BusinessServiceHoursRepository(ABC):
    @abstractmethod
    def create(self, business_service_hours: BusinessServiceHours) -> BusinessServiceHours:
        pass

    @abstractmethod
    def get_by_role(self, role_id: UUID) -> list[BusinessServiceHours]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> list[BusinessServiceHours]:
        pass

    @abstractmethod
    def get_all(self) -> list[BusinessServiceHours]:
        pass

    @abstractmethod
    def get_by_id(self, business_service_hours_id: UUID) -> BusinessServiceHours | None:
        pass

    @abstractmethod
    def delete(self, business_service_hours_id: UUID) -> bool:
        pass


class AgendaRepository(ABC):
    @abstractmethod
    def create(self, agenda: Agenda) -> Agenda:
        pass

    @abstractmethod
    def get_by_id(self, agenda_id: UUID) -> Agenda | None:
        pass

    @abstractmethod
    def get_by_role(self, role_id: UUID) -> list[Agenda]:
        pass

    @abstractmethod
    def get_by_role_and_status(self, role_id: UUID, status: str) -> list[Agenda]:
        pass

    @abstractmethod
    def create_entry(self, entry: AgendaEntry) -> AgendaEntry:
        pass

    @abstractmethod
    def get_entries_by_agenda(self, agenda_id: UUID) -> list[AgendaEntry]:
        pass

    @abstractmethod
    def create_coverage(self, coverage: AgendaCoverage) -> AgendaCoverage:
        pass

    @abstractmethod
    def get_coverage_by_agenda(self, agenda_id: UUID) -> list[AgendaCoverage]:
        pass

    @abstractmethod
    def update_status(self, agenda_id: UUID, status: str) -> bool:
        pass

