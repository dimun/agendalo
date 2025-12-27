from datetime import date, timedelta
from uuid import UUID

from modules.main_backend.domain.models import AvailabilityHours, Person, Role
from modules.main_backend.domain.schemas import CalendarEntry
from modules.main_backend.repositories.interfaces import (
    AvailabilityHoursRepository,
    PersonRepository,
    RoleRepository,
)


class CalendarService:
    def __init__(
        self,
        availability_hours_repository: AvailabilityHoursRepository,
        person_repository: PersonRepository,
        role_repository: RoleRepository,
    ):
        self.availability_hours_repository = availability_hours_repository
        self.person_repository = person_repository
        self.role_repository = role_repository

    def get_calendar_week(self, week: int, year: int) -> list[CalendarEntry]:
        start_date = self._get_week_start_date(week, year)
        end_date = start_date + timedelta(days=6)

        availability_hours_list = self.availability_hours_repository.get_by_date_range(
            start_date, end_date
        )

        entries = []
        people_cache: dict[UUID, Person] = {}
        roles_cache: dict[UUID, Role] = {}

        for current_date in self._date_range(start_date, end_date):
            day_of_week = current_date.weekday()

            for ah in availability_hours_list:
                if self._matches_date(ah, current_date, day_of_week):
                    if ah.person_id not in people_cache:
                        person = self.person_repository.get_by_id(ah.person_id)
                        if person:
                            people_cache[ah.person_id] = person

                    if ah.role_id not in roles_cache:
                        role = self.role_repository.get_by_id(ah.role_id)
                        if role:
                            roles_cache[ah.role_id] = role

                    person = people_cache.get(ah.person_id)
                    role = roles_cache.get(ah.role_id)

                    if person and role:
                        entries.append(
                            CalendarEntry(
                                date=current_date,
                                person_id=person.id,
                                person_name=person.name,
                                role_id=role.id,
                                role_name=role.name,
                                start_time=ah.start_time,
                                end_time=ah.end_time,
                            )
                        )

        return sorted(entries, key=lambda e: (e.date, e.start_time))

    def get_calendar_month(self, month: int, year: int) -> list[CalendarEntry]:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        availability_hours_list = self.availability_hours_repository.get_by_date_range(
            start_date, end_date
        )

        entries = []
        people_cache: dict[UUID, Person] = {}
        roles_cache: dict[UUID, Role] = {}

        for current_date in self._date_range(start_date, end_date):
            day_of_week = current_date.weekday()

            for ah in availability_hours_list:
                if self._matches_date(ah, current_date, day_of_week):
                    if ah.person_id not in people_cache:
                        person = self.person_repository.get_by_id(ah.person_id)
                        if person:
                            people_cache[ah.person_id] = person

                    if ah.role_id not in roles_cache:
                        role = self.role_repository.get_by_id(ah.role_id)
                        if role:
                            roles_cache[ah.role_id] = role

                    person = people_cache.get(ah.person_id)
                    role = roles_cache.get(ah.role_id)

                    if person and role:
                        entries.append(
                            CalendarEntry(
                                date=current_date,
                                person_id=person.id,
                                person_name=person.name,
                                role_id=role.id,
                                role_name=role.name,
                                start_time=ah.start_time,
                                end_time=ah.end_time,
                            )
                        )

        return sorted(entries, key=lambda e: (e.date, e.start_time))

    def _matches_date(self, ah: AvailabilityHours, current_date: date, day_of_week: int) -> bool:
        if ah.specific_date:
            return ah.specific_date == current_date

        if ah.is_recurring and ah.day_of_week is not None:
            if ah.day_of_week != day_of_week:
                return False

            if ah.start_date and current_date < ah.start_date:
                return False

            if ah.end_date and current_date > ah.end_date:
                return False

            return True

        if ah.start_date and ah.end_date:
            return ah.start_date <= current_date <= ah.end_date

        return False

    def _get_week_start_date(self, week: int, year: int) -> date:
        jan1 = date(year, 1, 1)
        jan1_weekday = jan1.weekday()
        days_to_monday = (jan1_weekday - 0) % 7
        first_monday = jan1 - timedelta(days=days_to_monday)

        if first_monday.year < year:
            first_monday = first_monday + timedelta(weeks=1)

        week_start = first_monday + timedelta(weeks=week - 1)
        return week_start

    def _date_range(self, start: date, end: date):
        current = start
        while current <= end:
            yield current
            current += timedelta(days=1)

