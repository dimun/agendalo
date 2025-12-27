from datetime import date, time
from uuid import UUID, uuid4

import pytest

from app.domain.models import AvailabilityHours, BusinessServiceHours
from app.schedulers.or_tools_scheduler import ORToolsScheduler


@pytest.fixture
def scheduler():
    return ORToolsScheduler()


@pytest.fixture
def role_id() -> UUID:
    return uuid4()


@pytest.fixture
def person1_id() -> UUID:
    return uuid4()


@pytest.fixture
def person2_id() -> UUID:
    return uuid4()


@pytest.fixture
def person3_id() -> UUID:
    return uuid4()


class TestORToolsScheduler:
    def test_optimize_with_empty_availability_hours(self, scheduler, role_id):
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        result = scheduler.optimize([], business_service_hours, [1], 2024, "maximize_coverage")
        assert result == []

    def test_optimize_with_empty_business_service_hours(self, scheduler, person1_id, role_id):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        result = scheduler.optimize(availability_hours, [], [1], 2024, "maximize_coverage")
        assert result == []

    def test_optimize_single_person_single_slot_maximize_coverage(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert result[0].person_id == person1_id
        assert result[0].role_id == role_id
        assert result[0].start_time == time(9, 0)
        assert result[0].end_time == time(17, 0)

    def test_optimize_multiple_people_single_slot_maximize_coverage(
        self, scheduler, person1_id, person2_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person2_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        person_ids = {assignment.person_id for assignment in result}
        assert person1_id in person_ids or person2_id in person_ids

    def test_optimize_person_not_available_should_not_be_assigned(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) == 0

    def test_optimize_specific_date_matching(
        self, scheduler, person1_id, role_id
    ):
        specific_date = date(2024, 1, 1)
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=None,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=False,
                specific_date=specific_date,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=None,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=False,
                specific_date=specific_date,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert result[0].date == specific_date

    def test_optimize_multiple_weeks(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1, 2], 2024, "maximize_coverage"
        )

        assert len(result) >= 2
        dates = {assignment.date for assignment in result}
        assert len(dates) >= 2

    def test_optimize_minimize_gaps_strategy(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(13, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(13, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "minimize_gaps"
        )

        assert len(result) >= 2

    def test_optimize_balance_workload_strategy(
        self, scheduler, person1_id, person2_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person2_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person2_id,
                role_id=role_id,
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "balance_workload"
        )

        assert len(result) >= 2
        person1_assignments = [
            a for a in result if a.person_id == person1_id
        ]
        person2_assignments = [
            a for a in result if a.person_id == person2_id
        ]
        assert len(person1_assignments) > 0
        assert len(person2_assignments) > 0

    def test_optimize_no_overlapping_assignments(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(10, 0),
                end_time=time(13, 0),
                is_recurring=True,
            ),
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        if len(result) > 1:
            for i, assignment1 in enumerate(result):
                for assignment2 in result[i + 1 :]:
                    if assignment1.date == assignment2.date:
                        assert not self._times_overlap(
                            assignment1.start_time,
                            assignment1.end_time,
                            assignment2.start_time,
                            assignment2.end_time,
                        )

    def test_optimize_partial_availability_coverage(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(13, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(13, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert all(
            assignment.start_time >= time(9, 0) and assignment.end_time <= time(13, 0)
            for assignment in result
        )

    def test_optimize_date_range_business_hours(
        self, scheduler, person1_id, role_id
    ):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 5)
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=None,
                start_time=time(9, 0),
                end_time=time(17, 0),
                start_date=start_date,
                end_date=end_date,
                is_recurring=False,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=None,
                start_time=time(9, 0),
                end_time=time(17, 0),
                start_date=start_date,
                end_date=end_date,
                is_recurring=False,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        for assignment in result:
            assert start_date <= assignment.date <= end_date

    def test_optimize_invalid_strategy_still_returns_solution(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "invalid_strategy"
        )

        assert len(result) > 0

    def test_optimize_multiple_roles_separate(
        self, scheduler, person1_id
    ):
        role1_id = uuid4()
        role2_id = uuid4()

        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role1_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role1_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert all(assignment.role_id == role1_id for assignment in result)

    def test_optimize_early_morning_shift(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(6, 0),
                end_time=time(14, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(6, 0),
                end_time=time(14, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert result[0].start_time == time(6, 0)
        assert result[0].end_time == time(14, 0)

    def test_optimize_late_night_shift(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(18, 0),
                end_time=time(23, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert result[0].start_time == time(18, 0)
        assert result[0].end_time == time(23, 0)

    def test_optimize_short_shift(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=0,
                start_time=time(10, 0),
                end_time=time(11, 0),
                is_recurring=True,
            )
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(10, 0),
                end_time=time(11, 0),
                is_recurring=True,
            )
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) > 0
        assert result[0].start_time == time(10, 0)
        assert result[0].end_time == time(11, 0)

    def test_optimize_all_weekdays(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
            for day in range(5)
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            )
            for day in range(5)
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) >= 5
        weekdays = {assignment.date.weekday() for assignment in result}
        assert len(weekdays) >= 5

    def test_optimize_weekend_only(
        self, scheduler, person1_id, role_id
    ):
        availability_hours = [
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=5,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            AvailabilityHours(
                id=uuid4(),
                person_id=person1_id,
                role_id=role_id,
                day_of_week=6,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=5,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=6,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "maximize_coverage"
        )

        assert len(result) >= 2
        for assignment in result:
            assert assignment.date.weekday() in [5, 6]

    def test_optimize_three_people_balance_workload(
        self, scheduler, person1_id, person2_id, person3_id, role_id
    ):
        availability_hours = []
        for person_id in [person1_id, person2_id, person3_id]:
            for day in [0, 1, 2]:
                availability_hours.append(
                    AvailabilityHours(
                        id=uuid4(),
                        person_id=person_id,
                        role_id=role_id,
                        day_of_week=day,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        is_recurring=True,
                    )
                )
        business_service_hours = [
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=1,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
            BusinessServiceHours(
                id=uuid4(),
                role_id=role_id,
                day_of_week=2,
                start_time=time(9, 0),
                end_time=time(17, 0),
                is_recurring=True,
            ),
        ]

        result = scheduler.optimize(
            availability_hours, business_service_hours, [1], 2024, "balance_workload"
        )

        assert len(result) >= 3
        person_assignments = {}
        for assignment in result:
            person_assignments[assignment.person_id] = (
                person_assignments.get(assignment.person_id, 0) + 1
            )
        assert len(person_assignments) >= 2

    @staticmethod
    def _times_overlap(
        start1: time, end1: time, start2: time, end2: time
    ) -> bool:
        return not (end1 <= start2 or end2 <= start1)

