from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_availability_hours_service
from app.domain.schemas import AvailabilityHoursCreate, AvailabilityHoursResponse
from app.services.availability_hours_service import AvailabilityHoursService

router = APIRouter(prefix="/api", tags=["availability-hours"])


@router.post(
    "/people/{person_id}/availability-hours",
    response_model=AvailabilityHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_availability_hours(
    person_id: UUID,
    availability_hours_data: AvailabilityHoursCreate,
    availability_hours_service: AvailabilityHoursService = Depends(get_availability_hours_service),
):
    availability_hours = availability_hours_service.create_availability_hours(
        person_id, availability_hours_data
    )
    if not availability_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person or role not found",
        )
    return AvailabilityHoursResponse(
        id=availability_hours.id,
        person_id=availability_hours.person_id,
        role_id=availability_hours.role_id,
        day_of_week=availability_hours.day_of_week,
        start_time=availability_hours.start_time,
        end_time=availability_hours.end_time,
        start_date=availability_hours.start_date,
        end_date=availability_hours.end_date,
        is_recurring=availability_hours.is_recurring,
        specific_date=availability_hours.specific_date,
    )


@router.get(
    "/people/{person_id}/availability-hours",
    response_model=list[AvailabilityHoursResponse],
)
def get_availability_hours_by_person(
    person_id: UUID,
    availability_hours_service: AvailabilityHoursService = Depends(get_availability_hours_service),
):
    availability_hours_list = availability_hours_service.get_availability_hours_by_person(
        person_id
    )
    return [
        AvailabilityHoursResponse(
            id=ah.id,
            person_id=ah.person_id,
            role_id=ah.role_id,
            day_of_week=ah.day_of_week,
            start_time=ah.start_time,
            end_time=ah.end_time,
            start_date=ah.start_date,
            end_date=ah.end_date,
            is_recurring=ah.is_recurring,
            specific_date=ah.specific_date,
        )
        for ah in availability_hours_list
    ]


@router.get("/availability-hours", response_model=list[AvailabilityHoursResponse])
def get_availability_hours(
    role_id: UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    availability_hours_service: AvailabilityHoursService = Depends(get_availability_hours_service),
):
    if role_id:
        availability_hours_list = availability_hours_service.get_availability_hours_by_role(
            role_id
        )
    elif start_date and end_date:
        availability_hours_list = availability_hours_service.get_availability_hours_by_date_range(
            start_date.isoformat(), end_date.isoformat()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either role_id or both start_date and end_date must be provided",
        )

    return [
        AvailabilityHoursResponse(
            id=ah.id,
            person_id=ah.person_id,
            role_id=ah.role_id,
            day_of_week=ah.day_of_week,
            start_time=ah.start_time,
            end_time=ah.end_time,
            start_date=ah.start_date,
            end_date=ah.end_date,
            is_recurring=ah.is_recurring,
            specific_date=ah.specific_date,
        )
        for ah in availability_hours_list
    ]

