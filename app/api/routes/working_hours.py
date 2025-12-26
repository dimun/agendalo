from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_working_hours_service
from app.domain.schemas import WorkingHoursCreate, WorkingHoursResponse
from app.services.working_hours_service import WorkingHoursService

router = APIRouter(prefix="/api", tags=["working-hours"])


@router.post(
    "/people/{person_id}/working-hours",
    response_model=WorkingHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_working_hours(
    person_id: UUID,
    working_hours_data: WorkingHoursCreate,
    working_hours_service: WorkingHoursService = Depends(get_working_hours_service),
):
    working_hours = working_hours_service.create_working_hours(
        person_id, working_hours_data
    )
    if not working_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person or role not found",
        )
    return WorkingHoursResponse(
        id=working_hours.id,
        person_id=working_hours.person_id,
        role_id=working_hours.role_id,
        day_of_week=working_hours.day_of_week,
        start_time=working_hours.start_time,
        end_time=working_hours.end_time,
        start_date=working_hours.start_date,
        end_date=working_hours.end_date,
        is_recurring=working_hours.is_recurring,
        specific_date=working_hours.specific_date,
    )


@router.get(
    "/people/{person_id}/working-hours",
    response_model=list[WorkingHoursResponse],
)
def get_working_hours_by_person(
    person_id: UUID,
    working_hours_service: WorkingHoursService = Depends(get_working_hours_service),
):
    working_hours_list = working_hours_service.get_working_hours_by_person(
        person_id
    )
    return [
        WorkingHoursResponse(
            id=wh.id,
            person_id=wh.person_id,
            role_id=wh.role_id,
            day_of_week=wh.day_of_week,
            start_time=wh.start_time,
            end_time=wh.end_time,
            start_date=wh.start_date,
            end_date=wh.end_date,
            is_recurring=wh.is_recurring,
            specific_date=wh.specific_date,
        )
        for wh in working_hours_list
    ]


@router.get("/working-hours", response_model=list[WorkingHoursResponse])
def get_working_hours(
    role_id: UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    working_hours_service: WorkingHoursService = Depends(get_working_hours_service),
):
    if role_id:
        working_hours_list = working_hours_service.get_working_hours_by_role(
            role_id
        )
    elif start_date and end_date:
        working_hours_list = working_hours_service.get_working_hours_by_date_range(
            start_date.isoformat(), end_date.isoformat()
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either role_id or both start_date and end_date must be provided",
        )

    return [
        WorkingHoursResponse(
            id=wh.id,
            person_id=wh.person_id,
            role_id=wh.role_id,
            day_of_week=wh.day_of_week,
            start_time=wh.start_time,
            end_time=wh.end_time,
            start_date=wh.start_date,
            end_date=wh.end_date,
            is_recurring=wh.is_recurring,
            specific_date=wh.specific_date,
        )
        for wh in working_hours_list
    ]

