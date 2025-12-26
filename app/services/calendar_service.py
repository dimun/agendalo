from datetime import date, timedelta
from uuid import UUID

from app.domain.models import Person, Role, WorkingHours
from app.domain.schemas import CalendarEntry
from app.repositories.interfaces import (
    PersonRepository,
    RoleRepository,
    WorkingHoursRepository,
)


class CalendarService:
    def __init__(
        self,
        working_hours_repository: WorkingHoursRepository,
        person_repository: PersonRepository,
        role_repository: RoleRepository,
    ):
        self.working_hours_repository = working_hours_repository
        self.person_repository = person_repository
        self.role_repository = role_repository

    def get_calendar_week(self, week: int, year: int) -> list[CalendarEntry]:
        start_date = self._get_week_start_date(week, year)
        end_date = start_date + timedelta(days=6)

        working_hours_list = self.working_hours_repository.get_by_date_range(
            start_date, end_date
        )

        entries = []
        people_cache: dict[UUID, Person] = {}
        roles_cache: dict[UUID, Role] = {}

        for current_date in self._date_range(start_date, end_date):
            day_of_week = current_date.weekday()

            for wh in working_hours_list:
                if self._matches_date(wh, current_date, day_of_week):
                    if wh.person_id not in people_cache:
                        person = self.person_repository.get_by_id(wh.person_id)
                        if person:
                            people_cache[wh.person_id] = person

                    if wh.role_id not in roles_cache:
                        role = self.role_repository.get_by_id(wh.role_id)
                        if role:
                            roles_cache[wh.role_id] = role

                    person = people_cache.get(wh.person_id)
                    role = roles_cache.get(wh.role_id)

                    if person and role:
                        entries.append(
                            CalendarEntry(
                                date=current_date,
                                person_id=person.id,
                                person_name=person.name,
                                role_id=role.id,
                                role_name=role.name,
                                start_time=wh.start_time,
                                end_time=wh.end_time,
                            )
                        )

        return sorted(entries, key=lambda e: (e.date, e.start_time))

    def get_calendar_month(self, month: int, year: int) -> list[CalendarEntry]:
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)

        working_hours_list = self.working_hours_repository.get_by_date_range(
            start_date, end_date
        )

        entries = []
        people_cache: dict[UUID, Person] = {}
        roles_cache: dict[UUID, Role] = {}

        for current_date in self._date_range(start_date, end_date):
            day_of_week = current_date.weekday()

            for wh in working_hours_list:
                if self._matches_date(wh, current_date, day_of_week):
                    if wh.person_id not in people_cache:
                        person = self.person_repository.get_by_id(wh.person_id)
                        if person:
                            people_cache[wh.person_id] = person

                    if wh.role_id not in roles_cache:
                        role = self.role_repository.get_by_id(wh.role_id)
                        if role:
                            roles_cache[wh.role_id] = role

                    person = people_cache.get(wh.person_id)
                    role = roles_cache.get(wh.role_id)

                    if person and role:
                        entries.append(
                            CalendarEntry(
                                date=current_date,
                                person_id=person.id,
                                person_name=person.name,
                                role_id=role.id,
                                role_name=role.name,
                                start_time=wh.start_time,
                                end_time=wh.end_time,
                            )
                        )

        return sorted(entries, key=lambda e: (e.date, e.start_time))

    def _matches_date(self, wh: WorkingHours, current_date: date, day_of_week: int) -> bool:
        if wh.specific_date:
            return wh.specific_date == current_date

        if wh.is_recurring and wh.day_of_week is not None:
            if wh.day_of_week != day_of_week:
                return False

            if wh.start_date and current_date < wh.start_date:
                return False

            if wh.end_date and current_date > wh.end_date:
                return False

            return True

        if wh.start_date and wh.end_date:
            return wh.start_date <= current_date <= wh.end_date

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

