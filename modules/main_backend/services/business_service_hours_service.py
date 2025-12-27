from datetime import date
from uuid import UUID, uuid4

from modules.main_backend.domain.models import BusinessServiceHours
from modules.main_backend.domain.schemas import BusinessServiceHoursCreate, BusinessServiceHoursBulkCreate
from modules.main_backend.repositories.interfaces import (
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

    def get_business_service_hours_by_role_and_date_range(
        self, role_id: UUID, start_date: str, end_date: str
    ) -> list[BusinessServiceHours]:
        all_by_role = self.business_service_hours_repository.get_by_role(role_id)
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        
        filtered = []
        for bsh in all_by_role:
            if bsh.is_recurring and bsh.day_of_week is not None:
                if bsh.start_date and bsh.start_date > end:
                    continue
                if bsh.end_date and bsh.end_date < start:
                    continue
                filtered.append(bsh)
            elif bsh.specific_date:
                if start <= bsh.specific_date <= end:
                    filtered.append(bsh)
            elif bsh.start_date and bsh.end_date:
                if not (bsh.end_date < start or bsh.start_date > end):
                    filtered.append(bsh)
        
        return filtered

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

    def create_business_service_hours_bulk(
        self, bulk_data: BusinessServiceHoursBulkCreate
    ) -> list[BusinessServiceHours]:
        role = self.role_repository.get_by_id(bulk_data.role_id)
        if not role:
            return []

        days_to_create = self._parse_days(bulk_data.days)
        if not days_to_create:
            return []

        created_hours = []
        for day_of_week in days_to_create:
            business_service_hours = BusinessServiceHours(
                id=uuid4(),
                role_id=bulk_data.role_id,
                day_of_week=day_of_week,
                start_time=bulk_data.start_time,
                end_time=bulk_data.end_time,
                start_date=bulk_data.start_date,
                end_date=bulk_data.end_date,
                is_recurring=True,
                specific_date=None,
            )
            created = self.business_service_hours_repository.create(business_service_hours)
            created_hours.append(created)

        return created_hours

    def _parse_days(self, days: str) -> list[int]:
        days_lower = days.lower().strip()
        
        if days_lower == "all":
            return list(range(7))
        
        day_map = {
            "mon": 0, "tue": 1, "wed": 2, "thu": 3,
            "fri": 4, "sat": 5, "sun": 6
        }
        
        if "-" in days_lower:
            parts = days_lower.split("-")
            if len(parts) != 2:
                return []
            
            start_day = parts[0].strip()
            end_day = parts[1].strip()
            
            if start_day not in day_map or end_day not in day_map:
                return []
            
            start_idx = day_map[start_day]
            end_idx = day_map[end_day]
            
            if start_idx <= end_idx:
                return list(range(start_idx, end_idx + 1))
            else:
                return list(range(start_idx, 7)) + list(range(0, end_idx + 1))
        
        return []

