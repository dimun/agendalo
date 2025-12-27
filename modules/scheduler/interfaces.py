from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, time
from uuid import UUID

from modules.scheduler.models import AvailabilityHours, BusinessServiceHours


@dataclass
class Assignment:
    person_id: UUID
    date: date
    start_time: time
    end_time: time
    role_id: UUID


class Scheduler(ABC):
    @abstractmethod
    def optimize(
        self,
        availability_hours: list[AvailabilityHours],
        business_service_hours: list[BusinessServiceHours],
        weeks: list[int],
        year: int,
        strategy: str,
    ) -> list[Assignment]:
        pass

