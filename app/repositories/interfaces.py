from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from app.domain.models import BusinessServiceHours, Person, Role, WorkingHours


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


class WorkingHoursRepository(ABC):
    @abstractmethod
    def create(self, working_hours: WorkingHours) -> WorkingHours:
        pass

    @abstractmethod
    def get_by_person(self, person_id: UUID) -> list[WorkingHours]:
        pass

    @abstractmethod
    def get_by_role(self, role_id: UUID) -> list[WorkingHours]:
        pass

    @abstractmethod
    def get_by_date_range(self, start_date: date, end_date: date) -> list[WorkingHours]:
        pass

    @abstractmethod
    def delete(self, working_hours_id: UUID) -> bool:
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

