from collections import defaultdict
from datetime import date, datetime, timedelta, time
from typing import Dict, List, Set, Tuple
from uuid import UUID

from ortools.sat.python import cp_model

from app.domain.models import AvailabilityHours, BusinessServiceHours
from app.schedulers.interfaces import Assignment, Scheduler


class ORToolsScheduler(Scheduler):
    def optimize(
        self,
        availability_hours: list[AvailabilityHours],
        business_service_hours: list[BusinessServiceHours],
        weeks: list[int],
        year: int,
        strategy: str,
    ) -> list[Assignment]:
        if not availability_hours or not business_service_hours:
            return []

        date_range = self._get_date_range_for_weeks(weeks, year)
        time_slots = self._create_time_slots(business_service_hours, date_range)
        availability_slots = self._create_availability_slots(
            availability_hours, date_range
        )

        if not time_slots or not availability_slots:
            return []

        model = cp_model.CpModel()

        person_ids = {ah.person_id for ah in availability_hours}
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar] = {}

        for person_id in person_ids:
            for slot_date, slot_start, slot_end in time_slots:
                var_name = f"assign_{person_id}_{slot_date}_{slot_start}_{slot_end}"
                assignments[(person_id, slot_date, slot_start, slot_end)] = (
                    model.NewBoolVar(var_name)
                )

        for slot_date, slot_start, slot_end in time_slots:
            person_assignments = [
                assignments[(pid, slot_date, slot_start, slot_end)]
                for pid in person_ids
                if (pid, slot_date, slot_start, slot_end) in assignments
            ]
            if person_assignments:
                model.Add(sum(person_assignments) >= 1)

        for person_id in person_ids:
            for slot_date, slot_start, slot_end in time_slots:
                if (person_id, slot_date, slot_start, slot_end) not in assignments:
                    continue

                is_available = self._is_person_available(
                    person_id, slot_date, slot_start, slot_end, availability_slots
                )
                if not is_available:
                    model.Add(assignments[(person_id, slot_date, slot_start, slot_end)] == 0)

        for person_id in person_ids:
            for slot_date, slot_start, slot_end in time_slots:
                if (person_id, slot_date, slot_start, slot_end) not in assignments:
                    continue

                overlapping_slots = self._get_overlapping_slots(
                    slot_date, slot_start, slot_end, time_slots
                )
                for overlap_date, overlap_start, overlap_end in overlapping_slots:
                    if (person_id, overlap_date, overlap_start, overlap_end) in assignments:
                        if (overlap_date, overlap_start, overlap_end) != (
                            slot_date,
                            slot_start,
                            slot_end,
                        ):
                            model.Add(
                                assignments[(person_id, slot_date, slot_start, slot_end)]
                                + assignments[
                                    (person_id, overlap_date, overlap_start, overlap_end)
                                ]
                                <= 1
                            )

        objective_terms = self._build_objective(
            model, strategy, time_slots, person_ids, assignments
        )

        if objective_terms:
            model.Maximize(sum(objective_terms))

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            assignments_list = []
            role_id = business_service_hours[0].role_id
            for (person_id, slot_date, slot_start, slot_end), var in assignments.items():
                if solver.Value(var) == 1:
                    assignments_list.append(
                        Assignment(
                            person_id=person_id,
                            date=slot_date,
                            start_time=slot_start,
                            end_time=slot_end,
                            role_id=role_id,
                        )
                    )
            return assignments_list

        return []

    def _get_date_range_for_weeks(self, weeks: list[int], year: int) -> List[date]:
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

    def _create_time_slots(
        self, business_service_hours: list[BusinessServiceHours], date_range: List[date]
    ) -> List[Tuple[date, time, time]]:
        slots = []
        for bsh in business_service_hours:
            for d in date_range:
                day_of_week = d.weekday()
                if bsh.specific_date:
                    if bsh.specific_date == d:
                        slots.append((d, bsh.start_time, bsh.end_time))
                elif bsh.is_recurring and bsh.day_of_week is not None:
                    if bsh.day_of_week == day_of_week:
                        if not bsh.start_date or d >= bsh.start_date:
                            if not bsh.end_date or d <= bsh.end_date:
                                slots.append((d, bsh.start_time, bsh.end_time))
                elif bsh.start_date and bsh.end_date:
                    if bsh.start_date <= d <= bsh.end_date:
                        slots.append((d, bsh.start_time, bsh.end_time))
        return sorted(set(slots))

    def _create_availability_slots(
        self, availability_hours: list[AvailabilityHours], date_range: List[date]
    ) -> Set[Tuple[UUID, date, time, time]]:
        slots = set()
        for ah in availability_hours:
            for d in date_range:
                day_of_week = d.weekday()
                if ah.specific_date:
                    if ah.specific_date == d:
                        slots.add((ah.person_id, d, ah.start_time, ah.end_time))
                elif ah.is_recurring and ah.day_of_week is not None:
                    if ah.day_of_week == day_of_week:
                        if not ah.start_date or d >= ah.start_date:
                            if not ah.end_date or d <= ah.end_date:
                                slots.add((ah.person_id, d, ah.start_time, ah.end_time))
                elif ah.start_date and ah.end_date:
                    if ah.start_date <= d <= ah.end_date:
                        slots.add((ah.person_id, d, ah.start_time, ah.end_time))
        return slots

    def _is_person_available(
        self,
        person_id: UUID,
        slot_date: date,
        slot_start: time,
        slot_end: time,
        availability_slots: Set[Tuple[UUID, date, time, time]],
    ) -> bool:
        for pid, avail_date, avail_start, avail_end in availability_slots:
            if pid == person_id and avail_date == slot_date:
                if avail_start <= slot_start and slot_end <= avail_end:
                    return True
        return False

    def _get_overlapping_slots(
        self, slot_date: date, slot_start: time, slot_end: time, all_slots: List[Tuple[date, time, time]]
    ) -> List[Tuple[date, time, time]]:
        overlapping = []
        for other_date, other_start, other_end in all_slots:
            if other_date == slot_date:
                if not (slot_end <= other_start or other_end <= slot_start):
                    overlapping.append((other_date, other_start, other_end))
        return overlapping

    def _calculate_gap(
        self, date1: date, time1: time, date2: date, time2: time
    ) -> int:
        dt1 = datetime.combine(date1, time1)
        dt2 = datetime.combine(date2, time2)
        return int((dt2 - dt1).total_seconds() / 3600)

    def _calculate_duration(self, start_time: time, end_time: time) -> int:
        start_dt = datetime.combine(date.today(), start_time)
        end_dt = datetime.combine(date.today(), end_time)
        if end_dt < start_dt:
            end_dt += timedelta(days=1)
        return int((end_dt - start_dt).total_seconds() / 3600)

    def _build_objective(
        self,
        model: cp_model.CpModel,
        strategy: str,
        time_slots: List[Tuple[date, time, time]],
        person_ids: Set[UUID],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar | cp_model.IntVar]:
        strategy_builders = {
            "maximize_coverage": self._build_maximize_coverage_objective,
            "minimize_gaps": self._build_minimize_gaps_objective,
            "balance_workload": self._build_balance_workload_objective,
        }

        builder = strategy_builders.get(strategy)
        if builder:
            return builder(model, time_slots, person_ids, assignments)
        return []

    def _build_maximize_coverage_objective(
        self,
        model: cp_model.CpModel,
        time_slots: List[Tuple[date, time, time]],
        person_ids: Set[UUID],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        objective_terms = []
        for slot_date, slot_start, slot_end in time_slots:
            slot_covered = model.NewBoolVar(f"covered_{slot_date}_{slot_start}_{slot_end}")
            person_assignments = [
                assignments[(pid, slot_date, slot_start, slot_end)]
                for pid in person_ids
                if (pid, slot_date, slot_start, slot_end) in assignments
            ]
            if person_assignments:
                model.AddMaxEquality(slot_covered, person_assignments)
                objective_terms.append(slot_covered)
        return objective_terms

    def _build_minimize_gaps_objective(
        self,
        model: cp_model.CpModel,
        time_slots: List[Tuple[date, time, time]],
        person_ids: Set[UUID],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        gap_terms = []
        for person_id in person_ids:
            person_gap_terms = self._calculate_person_gaps(
                model, person_id, time_slots, assignments
            )
            gap_terms.extend(person_gap_terms)

        if not gap_terms:
            return []

        gap_penalty = model.NewIntVar(0, 1000000, "gap_penalty")
        model.Add(gap_penalty == sum(gap_terms))
        return [-gap_penalty]

    def _calculate_person_gaps(
        self,
        model: cp_model.CpModel,
        person_id: UUID,
        time_slots: List[Tuple[date, time, time]],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        person_slots = [
            (slot_date, slot_start, slot_end)
            for slot_date, slot_start, slot_end in time_slots
            if (person_id, slot_date, slot_start, slot_end) in assignments
        ]
        person_slots.sort()

        gap_terms = []
        for i in range(len(person_slots) - 1):
            slot1_date, slot1_start, slot1_end = person_slots[i]
            slot2_date, slot2_start, slot2_end = person_slots[i + 1]

            gap = self._calculate_gap(slot1_date, slot1_end, slot2_date, slot2_start)
            assigned1 = assignments[(person_id, slot1_date, slot1_start, slot1_end)]
            assigned2 = assignments[(person_id, slot2_date, slot2_start, slot2_end)]

            gap_var = model.NewIntVar(0, 10000, f"gap_{person_id}_{i}")
            model.Add(gap_var == gap).OnlyEnforceIf([assigned1, assigned2])
            model.Add(gap_var == 0).OnlyEnforceIf(assigned1.Not())
            model.Add(gap_var == 0).OnlyEnforceIf(assigned2.Not())
            gap_terms.append(gap_var)

        return gap_terms

    def _build_balance_workload_objective(
        self,
        model: cp_model.CpModel,
        time_slots: List[Tuple[date, time, time]],
        person_ids: Set[UUID],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        person_total_hours = self._calculate_person_total_hours(
            model, person_ids, time_slots, assignments
        )

        if len(person_total_hours) <= 1:
            return []

        return self._build_variance_penalty(model, person_total_hours)

    def _calculate_person_total_hours(
        self,
        model: cp_model.CpModel,
        person_ids: Set[UUID],
        time_slots: List[Tuple[date, time, time]],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> Dict[UUID, cp_model.IntVar]:
        person_total_hours = {}
        for person_id in person_ids:
            person_hours_list = self._calculate_person_slot_hours(
                model, person_id, time_slots, assignments
            )
            if person_hours_list:
                total = model.NewIntVar(0, 10000, f"total_{person_id}")
                model.Add(total == sum(person_hours_list))
                person_total_hours[person_id] = total
        return person_total_hours

    def _calculate_person_slot_hours(
        self,
        model: cp_model.CpModel,
        person_id: UUID,
        time_slots: List[Tuple[date, time, time]],
        assignments: Dict[Tuple[UUID, date, time, time], cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        person_hours_list = []
        for slot_date, slot_start, slot_end in time_slots:
            if (person_id, slot_date, slot_start, slot_end) not in assignments:
                continue

            duration = self._calculate_duration(slot_start, slot_end)
            hour_var = model.NewIntVar(0, duration, f"hours_{person_id}_{slot_date}")
            assignment_var = assignments[(person_id, slot_date, slot_start, slot_end)]

            model.Add(hour_var == duration).OnlyEnforceIf(assignment_var)
            model.Add(hour_var == 0).OnlyEnforceIf(assignment_var.Not())
            person_hours_list.append(hour_var)

        return person_hours_list

    def _build_variance_penalty(
        self,
        model: cp_model.CpModel,
        person_total_hours: Dict[UUID, cp_model.IntVar],
    ) -> List[cp_model.IntVar]:
        total_hours_list = list(person_total_hours.values())
        total_sum = model.NewIntVar(0, 100000, "total_sum")
        model.Add(total_sum == sum(total_hours_list))

        mean_var = model.NewIntVar(0, 10000, "mean_hours")
        model.AddDivisionEquality(mean_var, total_sum, len(total_hours_list))

        variance_terms = []
        for hours_var in total_hours_list:
            diff = model.NewIntVar(0, 10000, f"diff_{hours_var}")
            model.AddAbsEquality(diff, hours_var - mean_var)
            variance_terms.append(diff)

        if not variance_terms:
            return []

        variance_penalty = model.NewIntVar(0, 1000000, "variance_penalty")
        model.Add(variance_penalty == sum(variance_terms))
        return [-variance_penalty]

