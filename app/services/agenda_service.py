from collections import defaultdict
from datetime import date, datetime, timedelta, time
from uuid import UUID, uuid4

from app.domain.models import Agenda, AgendaCoverage, AgendaEntry
from app.repositories.interfaces import (
    AgendaRepository,
    AvailabilityHoursRepository,
    BusinessServiceHoursRepository,
    RoleRepository,
)
from app.schedulers.interfaces import Assignment, Scheduler


class AgendaService:
    def __init__(
        self,
        agenda_repository: AgendaRepository,
        availability_hours_repository: AvailabilityHoursRepository,
        business_service_hours_repository: BusinessServiceHoursRepository,
        role_repository: RoleRepository,
        scheduler: Scheduler,
    ):
        self.agenda_repository = agenda_repository
        self.availability_hours_repository = availability_hours_repository
        self.business_service_hours_repository = business_service_hours_repository
        self.role_repository = role_repository
        self.scheduler = scheduler

    def generate_draft_agenda(
        self, role_id: UUID, weeks: list[int], year: int, optimization_strategy: str
    ) -> Agenda | None:
        role = self.role_repository.get_by_id(role_id)
        if not role:
            return None

        date_range = self._get_date_range_for_weeks(weeks, year)
        if not date_range:
            return None

        start_date = min(date_range)
        end_date = max(date_range)

        availability_hours = self.availability_hours_repository.get_by_role(role_id)
        availability_hours = [
            ah
            for ah in availability_hours
            if self._overlaps_date_range(ah, start_date, end_date)
        ]

        business_service_hours = (
            self.business_service_hours_repository.get_by_role(role_id)
        )
        business_service_hours = [
            bsh
            for bsh in business_service_hours
            if self._overlaps_date_range(bsh, start_date, end_date)
        ]

        if not availability_hours or not business_service_hours:
            return None

        assignments = self.scheduler.optimize(
            availability_hours, business_service_hours, weeks, year, optimization_strategy
        )

        agenda = Agenda(
            id=uuid4(),
            role_id=role_id,
            status="draft",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        agenda = self.agenda_repository.create(agenda)

        for assignment in assignments:
            entry = AgendaEntry(
                id=uuid4(),
                agenda_id=agenda.id,
                person_id=assignment.person_id,
                date=assignment.date,
                start_time=assignment.start_time,
                end_time=assignment.end_time,
                role_id=assignment.role_id,
            )
            self.agenda_repository.create_entry(entry)

        coverage = self._calculate_coverage(
            business_service_hours, assignments, date_range, agenda.id, role_id
        )
        for cov in coverage:
            self.agenda_repository.create_coverage(cov)

        return agenda

    def get_agenda_with_details(self, agenda_id: UUID) -> Agenda | None:
        agenda = self.agenda_repository.get_by_id(agenda_id)
        return agenda

    def get_agendas_by_role(self, role_id: UUID, status: str | None = None) -> list[Agenda]:
        if status:
            return self.agenda_repository.get_by_role_and_status(role_id, status)
        return self.agenda_repository.get_by_role(role_id)

    def _get_date_range_for_weeks(self, weeks: list[int], year: int) -> list[date]:
        dates = []
        jan1 = date(year, 1, 1)
        jan1_weekday = jan1.weekday()
        days_to_monday = (jan1_weekday - 0) % 7
        first_monday = jan1 - timedelta(days=days_to_monday)
        if first_monday.year < year:
            first_monday = first_monday + timedelta(weeks=1)

        for week in weeks:
            week_start = first_monday + timedelta(weeks=week - 1)
            for day_offset in range(7):
                dates.append(week_start + timedelta(days=day_offset))
        return dates

    def _overlaps_date_range(self, item, start_date: date, end_date: date) -> bool:
        if item.specific_date:
            return start_date <= item.specific_date <= end_date
        if item.start_date and item.end_date:
            return not (item.end_date < start_date or item.start_date > end_date)
        if item.is_recurring and item.day_of_week is not None:
            return True
        return False

    def _calculate_coverage(
        self,
        business_service_hours: list,
        assignments: list[Assignment],
        date_range: list[date],
        agenda_id: UUID,
        role_id: UUID,
    ) -> list[AgendaCoverage]:
        coverage_list = []
        assignment_slots = {
            (a.date, a.start_time, a.end_time) for a in assignments
        }

        for bsh in business_service_hours:
            for d in date_range:
                day_of_week = d.weekday()
                if bsh.specific_date:
                    if bsh.specific_date == d:
                        slot = (d, bsh.start_time, bsh.end_time)
                        is_covered = slot in assignment_slots
                        coverage_list.append(
                            AgendaCoverage(
                                id=uuid4(),
                                agenda_id=agenda_id,
                                date=d,
                                start_time=bsh.start_time,
                                end_time=bsh.end_time,
                                role_id=role_id,
                                is_covered=is_covered,
                                required_person_count=1,
                            )
                        )
                elif bsh.is_recurring and bsh.day_of_week is not None:
                    if bsh.day_of_week == day_of_week:
                        if not bsh.start_date or d >= bsh.start_date:
                            if not bsh.end_date or d <= bsh.end_date:
                                slot = (d, bsh.start_time, bsh.end_time)
                                is_covered = slot in assignment_slots
                                coverage_list.append(
                                    AgendaCoverage(
                                        id=uuid4(),
                                        agenda_id=uuid4(),
                                        date=d,
                                        start_time=bsh.start_time,
                                        end_time=bsh.end_time,
                                        role_id=bsh.role_id,
                                        is_covered=is_covered,
                                        required_person_count=1,
                                    )
                                )
                elif bsh.start_date and bsh.end_date:
                    if bsh.start_date <= d <= bsh.end_date:
                        slot = (d, bsh.start_time, bsh.end_time)
                        is_covered = slot in assignment_slots
                        coverage_list.append(
                            AgendaCoverage(
                                id=uuid4(),
                                agenda_id=agenda_id,
                                date=d,
                                start_time=bsh.start_time,
                                end_time=bsh.end_time,
                                role_id=role_id,
                                is_covered=is_covered,
                                required_person_count=1,
                            )
                        )

        return coverage_list

