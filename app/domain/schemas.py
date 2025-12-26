from datetime import date, time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr


class PersonCreate(BaseModel):
    name: str
    email: EmailStr


class PersonResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: str


class RoleCreate(BaseModel):
    name: str
    description: str | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None = None


class WorkingHoursCreate(BaseModel):
    role_id: UUID
    day_of_week: int | None = None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool = True
    specific_date: date | None = None


class WorkingHoursResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    person_id: UUID
    role_id: UUID
    day_of_week: int | None = None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool
    specific_date: date | None = None


class CalendarEntry(BaseModel):
    date: date
    person_id: UUID
    person_name: str
    role_id: UUID
    role_name: str
    start_time: time
    end_time: time


class CalendarWeekResponse(BaseModel):
    week: int
    year: int
    entries: list[CalendarEntry]


class CalendarMonthResponse(BaseModel):
    month: int
    year: int
    entries: list[CalendarEntry]


class BusinessServiceHoursCreate(BaseModel):
    role_id: UUID
    day_of_week: int | None = None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool = True
    specific_date: date | None = None


class BusinessServiceHoursResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role_id: UUID
    day_of_week: int | None = None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool
    specific_date: date | None = None

