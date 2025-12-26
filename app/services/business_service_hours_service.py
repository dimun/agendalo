from datetime import date
from uuid import UUID, uuid4

from app.domain.models import BusinessServiceHours
from app.domain.schemas import BusinessServiceHoursCreate
from app.repositories.interfaces import (
    BusinessServiceHoursRepository,
    RoleRepository,
)


class BusinessServiceHoursService:
    def __init__(
        self,
        business_service_hours_repository: BusinessServiceHoursRepository,
        role_repository: RoleRepository,
    ):
        self.business_service_hours_repository = business_service_hours_repository
        self.role_repository = role_repository

    def create_business_service_hours(
        self, business_service_hours_data: BusinessServiceHoursCreate
    ) -> BusinessServiceHours | None:
        role = self.role_repository.get_by_id(business_service_hours_data.role_id)
        if not role:
            return None

        business_service_hours = BusinessServiceHours(
            id=uuid4(),
            role_id=business_service_hours_data.role_id,
            day_of_week=business_service_hours_data.day_of_week,
            start_time=business_service_hours_data.start_time,
            end_time=business_service_hours_data.end_time,
            start_date=business_service_hours_data.start_date,
            end_date=business_service_hours_data.end_date,
            is_recurring=business_service_hours_data.is_recurring,
            specific_date=business_service_hours_data.specific_date,
        )
        return self.business_service_hours_repository.create(business_service_hours)

    def get_business_service_hours_by_role(
        self, role_id: UUID
    ) -> list[BusinessServiceHours]:
        return self.business_service_hours_repository.get_by_role(role_id)

    def get_business_service_hours_by_date_range(
        self, start_date: str, end_date: str
    ) -> list[BusinessServiceHours]:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        return self.business_service_hours_repository.get_by_date_range(start, end)

    def get_all_business_service_hours(self) -> list[BusinessServiceHours]:
        return self.business_service_hours_repository.get_all()

    def get_business_service_hours_by_id(
        self, business_service_hours_id: UUID
    ) -> BusinessServiceHours | None:
        return self.business_service_hours_repository.get_by_id(business_service_hours_id)

    def delete_business_service_hours(
        self, business_service_hours_id: UUID
    ) -> bool:
        return self.business_service_hours_repository.delete(business_service_hours_id)

