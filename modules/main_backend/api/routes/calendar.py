from fastapi import APIRouter, Depends, Query

from modules.main_backend.api.dependencies import get_calendar_service
from modules.main_backend.domain.schemas import CalendarMonthResponse, CalendarWeekResponse
from modules.main_backend.services.calendar_service import CalendarService

router = APIRouter(prefix="/api/calendar", tags=["calendar"])


@router.get("/week", response_model=CalendarWeekResponse)
def get_calendar_week(
    week: int = Query(..., ge=1, le=53),
    year: int = Query(..., ge=2000, le=3000),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    entries = calendar_service.get_calendar_week(week, year)
    return CalendarWeekResponse(week=week, year=year, entries=entries)


@router.get("/month", response_model=CalendarMonthResponse)
def get_calendar_month(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2000, le=3000),
    calendar_service: CalendarService = Depends(get_calendar_service),
):
    entries = calendar_service.get_calendar_month(month, year)
    return CalendarMonthResponse(month=month, year=year, entries=entries)

