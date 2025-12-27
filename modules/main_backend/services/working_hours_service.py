from uuid import UUID, uuid4

from modules.main_backend.domain.models import AvailabilityHours
from modules.main_backend.domain.schemas import AvailabilityHoursCreate
from modules.main_backend.repositories.interfaces import (
    AvailabilityHoursRepository,
    PersonRepository,
    RoleRepository,
)


class AvailabilityHoursService:
    def __init__(
        self,
        availability_hours_repository: AvailabilityHoursRepository,
        person_repository: PersonRepository,
        role_repository: RoleRepository,
    ):
        self.availability_hours_repository = availability_hours_repository
        self.person_repository = person_repository
        self.role_repository = role_repository

    def create_availability_hours(
        self, person_id: UUID, availability_hours_data: AvailabilityHoursCreate
    ) -> AvailabilityHours | None:
        person = self.person_repository.get_by_id(person_id)
        if not person:
            return None

        role = self.role_repository.get_by_id(availability_hours_data.role_id)
        if not role:
            return None

        availability_hours = AvailabilityHours(
            id=uuid4(),
            person_id=person_id,
            role_id=availability_hours_data.role_id,
            day_of_week=availability_hours_data.day_of_week,
            start_time=availability_hours_data.start_time,
            end_time=availability_hours_data.end_time,
            start_date=availability_hours_data.start_date,
            end_date=availability_hours_data.end_date,
            is_recurring=availability_hours_data.is_recurring,
            specific_date=availability_hours_data.specific_date,
        )
        return self.availability_hours_repository.create(availability_hours)

    def get_availability_hours_by_person(self, person_id: UUID) -> list[AvailabilityHours]:
        return self.availability_hours_repository.get_by_person(person_id)

    def get_availability_hours_by_role(self, role_id: UUID) -> list[AvailabilityHours]:
        return self.availability_hours_repository.get_by_role(role_id)

    def get_availability_hours_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[AvailabilityHours]:
        from datetime import date

        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        return self.availability_hours_repository.get_by_date_range(start, end)

    def delete_availability_hours(self, availability_hours_id: UUID) -> bool:
        return self.availability_hours_repository.delete(availability_hours_id)

