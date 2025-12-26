from uuid import UUID, uuid4

from app.domain.models import WorkingHours
from app.domain.schemas import WorkingHoursCreate
from app.repositories.interfaces import PersonRepository, RoleRepository, WorkingHoursRepository


class WorkingHoursService:
    def __init__(
        self,
        working_hours_repository: WorkingHoursRepository,
        person_repository: PersonRepository,
        role_repository: RoleRepository,
    ):
        self.working_hours_repository = working_hours_repository
        self.person_repository = person_repository
        self.role_repository = role_repository

    def create_working_hours(
        self, person_id: UUID, working_hours_data: WorkingHoursCreate
    ) -> WorkingHours | None:
        person = self.person_repository.get_by_id(person_id)
        if not person:
            return None

        role = self.role_repository.get_by_id(working_hours_data.role_id)
        if not role:
            return None

        working_hours = WorkingHours(
            id=uuid4(),
            person_id=person_id,
            role_id=working_hours_data.role_id,
            day_of_week=working_hours_data.day_of_week,
            start_time=working_hours_data.start_time,
            end_time=working_hours_data.end_time,
            start_date=working_hours_data.start_date,
            end_date=working_hours_data.end_date,
            is_recurring=working_hours_data.is_recurring,
            specific_date=working_hours_data.specific_date,
        )
        return self.working_hours_repository.create(working_hours)

    def get_working_hours_by_person(self, person_id: UUID) -> list[WorkingHours]:
        return self.working_hours_repository.get_by_person(person_id)

    def get_working_hours_by_role(self, role_id: UUID) -> list[WorkingHours]:
        return self.working_hours_repository.get_by_role(role_id)

    def get_working_hours_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[WorkingHours]:
        from datetime import date

        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        return self.working_hours_repository.get_by_date_range(start, end)

    def delete_working_hours(self, working_hours_id: UUID) -> bool:
        return self.working_hours_repository.delete(working_hours_id)

