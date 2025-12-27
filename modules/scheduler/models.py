from dataclasses import dataclass
from datetime import date, time
from uuid import UUID


@dataclass
class AvailabilityHours:
    id: UUID
    person_id: UUID
    role_id: UUID
    day_of_week: int | None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool = True
    specific_date: date | None = None


@dataclass
class BusinessServiceHours:
    id: UUID
    role_id: UUID
    day_of_week: int | None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool = True
    specific_date: date | None = None

