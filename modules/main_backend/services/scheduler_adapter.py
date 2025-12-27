from modules.main_backend.domain.models import AvailabilityHours as DomainAvailabilityHours
from modules.main_backend.domain.models import BusinessServiceHours as DomainBusinessServiceHours
from modules.scheduler.models import AvailabilityHours as SchedulerAvailabilityHours
from modules.scheduler.models import BusinessServiceHours as SchedulerBusinessServiceHours


def to_scheduler_availability_hours(
    domain_ah: DomainAvailabilityHours,
) -> SchedulerAvailabilityHours:
    return SchedulerAvailabilityHours(
        id=domain_ah.id,
        person_id=domain_ah.person_id,
        role_id=domain_ah.role_id,
        day_of_week=domain_ah.day_of_week,
        start_time=domain_ah.start_time,
        end_time=domain_ah.end_time,
        start_date=domain_ah.start_date,
        end_date=domain_ah.end_date,
        is_recurring=domain_ah.is_recurring,
        specific_date=domain_ah.specific_date,
    )


def to_scheduler_business_service_hours(
    domain_bsh: DomainBusinessServiceHours,
) -> SchedulerBusinessServiceHours:
    return SchedulerBusinessServiceHours(
        id=domain_bsh.id,
        role_id=domain_bsh.role_id,
        day_of_week=domain_bsh.day_of_week,
        start_time=domain_bsh.start_time,
        end_time=domain_bsh.end_time,
        start_date=domain_bsh.start_date,
        end_date=domain_bsh.end_date,
        is_recurring=domain_bsh.is_recurring,
        specific_date=domain_bsh.specific_date,
    )

