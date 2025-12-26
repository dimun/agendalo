from dataclasses import dataclass
from datetime import date, time
from uuid import UUID


@dataclass
class Person:
    id: UUID
    name: str
    email: str


@dataclass
class Role:
    id: UUID
    name: str
    description: str | None = None


@dataclass
class WorkingHours:
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

