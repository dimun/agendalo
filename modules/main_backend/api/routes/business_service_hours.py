from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from modules.main_backend.api.dependencies import get_business_service_hours_service
from modules.main_backend.domain.schemas import (
    BusinessServiceHoursCreate,
    BusinessServiceHoursResponse,
)
from modules.main_backend.services.business_service_hours_service import BusinessServiceHoursService

router = APIRouter(prefix="/api/business-service-hours", tags=["business-service-hours"])


@router.post(
    "",
    response_model=BusinessServiceHoursResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_business_service_hours(
    business_service_hours_data: BusinessServiceHoursCreate,
    business_service_hours_service: BusinessServiceHoursService = Depends(
        get_business_service_hours_service
    ),
):
    business_service_hours = business_service_hours_service.create_business_service_hours(
        business_service_hours_data
    )
    if not business_service_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return BusinessServiceHoursResponse(
        id=business_service_hours.id,
        role_id=business_service_hours.role_id,
        day_of_week=business_service_hours.day_of_week,
        start_time=business_service_hours.start_time,
        end_time=business_service_hours.end_time,
        start_date=business_service_hours.start_date,
        end_date=business_service_hours.end_date,
        is_recurring=business_service_hours.is_recurring,
        specific_date=business_service_hours.specific_date,
    )


@router.get("", response_model=list[BusinessServiceHoursResponse])
def get_business_service_hours(
    role_id: UUID | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    business_service_hours_service: BusinessServiceHoursService = Depends(
        get_business_service_hours_service
    ),
):
    if role_id and start_date and end_date:
        business_service_hours_list = (
            business_service_hours_service.get_business_service_hours_by_role_and_date_range(
                role_id, start_date.isoformat(), end_date.isoformat()
            )
        )
    elif role_id:
        business_service_hours_list = (
            business_service_hours_service.get_business_service_hours_by_role(role_id)
        )
    elif start_date and end_date:
        business_service_hours_list = (
            business_service_hours_service.get_business_service_hours_by_date_range(
                start_date.isoformat(), end_date.isoformat()
            )
        )
    else:
        business_service_hours_list = (
            business_service_hours_service.get_all_business_service_hours()
        )

    return [
        BusinessServiceHoursResponse(
            id=bsh.id,
            role_id=bsh.role_id,
            day_of_week=bsh.day_of_week,
            start_time=bsh.start_time,
            end_time=bsh.end_time,
            start_date=bsh.start_date,
            end_date=bsh.end_date,
            is_recurring=bsh.is_recurring,
            specific_date=bsh.specific_date,
        )
        for bsh in business_service_hours_list
    ]


@router.get("/{business_service_hours_id}", response_model=BusinessServiceHoursResponse)
def get_business_service_hours_by_id(
    business_service_hours_id: UUID,
    business_service_hours_service: BusinessServiceHoursService = Depends(
        get_business_service_hours_service
    ),
):
    business_service_hours = (
        business_service_hours_service.get_business_service_hours_by_id(
            business_service_hours_id
        )
    )
    if not business_service_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business service hours not found",
        )
    return BusinessServiceHoursResponse(
        id=business_service_hours.id,
        role_id=business_service_hours.role_id,
        day_of_week=business_service_hours.day_of_week,
        start_time=business_service_hours.start_time,
        end_time=business_service_hours.end_time,
        start_date=business_service_hours.start_date,
        end_date=business_service_hours.end_date,
        is_recurring=business_service_hours.is_recurring,
        specific_date=business_service_hours.specific_date,
    )


@router.delete("/{business_service_hours_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_business_service_hours(
    business_service_hours_id: UUID,
    business_service_hours_service: BusinessServiceHoursService = Depends(
        get_business_service_hours_service
    ),
):
    deleted = business_service_hours_service.delete_business_service_hours(
        business_service_hours_id
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business service hours not found",
        )

