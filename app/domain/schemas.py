from datetime import date, datetime, time
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


class AvailabilityHoursCreate(BaseModel):
    role_id: UUID
    day_of_week: int | None = None
    start_time: time
    end_time: time
    start_date: date | None = None
    end_date: date | None = None
    is_recurring: bool = True
    specific_date: date | None = None


class AvailabilityHoursResponse(BaseModel):
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


class AgendaGenerateRequest(BaseModel):
    role_id: UUID
    weeks: list[int]
    year: int
    optimization_strategy: str


class AgendaEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agenda_id: UUID
    person_id: UUID
    date: date
    start_time: time
    end_time: time
    role_id: UUID


class AgendaCoverageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    agenda_id: UUID
    date: date
    start_time: time
    end_time: time
    role_id: UUID
    is_covered: bool
    required_person_count: int


class AgendaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role_id: UUID
    status: str
    created_at: datetime
    updated_at: datetime
    entries: list[AgendaEntryResponse] = []
    coverage: list[AgendaCoverageResponse] = []

