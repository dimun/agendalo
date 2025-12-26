from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_agenda_service
from app.domain.schemas import (
    AgendaCoverageResponse,
    AgendaEntryResponse,
    AgendaGenerateRequest,
    AgendaResponse,
)
from app.services.agenda_service import AgendaService

router = APIRouter(prefix="/api/agendas", tags=["agendas"])


@router.post("/generate", response_model=AgendaResponse, status_code=status.HTTP_201_CREATED)
def generate_agenda(
    request: AgendaGenerateRequest,
    agenda_service: AgendaService = Depends(get_agenda_service),
):
    if request.optimization_strategy not in [
        "maximize_coverage",
        "minimize_gaps",
        "balance_workload",
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid optimization strategy. Must be one of: maximize_coverage, minimize_gaps, balance_workload",
        )

    agenda = agenda_service.generate_draft_agenda(
        request.role_id,
        request.weeks,
        request.year,
        request.optimization_strategy,
    )

    if not agenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found or no availability/business service hours available",
        )

    entries = agenda_service.agenda_repository.get_entries_by_agenda(agenda.id)
    coverage = agenda_service.agenda_repository.get_coverage_by_agenda(agenda.id)

    return AgendaResponse(
        id=agenda.id,
        role_id=agenda.role_id,
        status=agenda.status,
        created_at=agenda.created_at,
        updated_at=agenda.updated_at,
        entries=[
            AgendaEntryResponse(
                id=e.id,
                agenda_id=e.agenda_id,
                person_id=e.person_id,
                date=e.date,
                start_time=e.start_time,
                end_time=e.end_time,
                role_id=e.role_id,
            )
            for e in entries
        ],
        coverage=[
            AgendaCoverageResponse(
                id=c.id,
                agenda_id=c.agenda_id,
                date=c.date,
                start_time=c.start_time,
                end_time=c.end_time,
                role_id=c.role_id,
                is_covered=c.is_covered,
                required_person_count=c.required_person_count,
            )
            for c in coverage
        ],
    )


@router.get("/{agenda_id}", response_model=AgendaResponse)
def get_agenda(
    agenda_id: UUID,
    agenda_service: AgendaService = Depends(get_agenda_service),
):
    agenda = agenda_service.get_agenda_with_details(agenda_id)
    if not agenda:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agenda not found",
        )

    entries = agenda_service.agenda_repository.get_entries_by_agenda(agenda.id)
    coverage = agenda_service.agenda_repository.get_coverage_by_agenda(agenda.id)

    return AgendaResponse(
        id=agenda.id,
        role_id=agenda.role_id,
        status=agenda.status,
        created_at=agenda.created_at,
        updated_at=agenda.updated_at,
        entries=[
            AgendaEntryResponse(
                id=e.id,
                agenda_id=e.agenda_id,
                person_id=e.person_id,
                date=e.date,
                start_time=e.start_time,
                end_time=e.end_time,
                role_id=e.role_id,
            )
            for e in entries
        ],
        coverage=[
            AgendaCoverageResponse(
                id=c.id,
                agenda_id=c.agenda_id,
                date=c.date,
                start_time=c.start_time,
                end_time=c.end_time,
                role_id=c.role_id,
                is_covered=c.is_covered,
                required_person_count=c.required_person_count,
            )
            for c in coverage
        ],
    )


@router.get("", response_model=list[AgendaResponse])
def get_agendas(
    role_id: UUID | None = Query(None),
    status: str | None = Query(None),
    agenda_service: AgendaService = Depends(get_agenda_service),
):
    if not role_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="role_id is required",
        )

    agendas = agenda_service.get_agendas_by_role(role_id, status)

    result = []
    for agenda in agendas:
        entries = agenda_service.agenda_repository.get_entries_by_agenda(agenda.id)
        coverage = agenda_service.agenda_repository.get_coverage_by_agenda(agenda.id)
        result.append(
            AgendaResponse(
                id=agenda.id,
                role_id=agenda.role_id,
                status=agenda.status,
                created_at=agenda.created_at,
                updated_at=agenda.updated_at,
                entries=[
                    AgendaEntryResponse(
                        id=e.id,
                        agenda_id=e.agenda_id,
                        person_id=e.person_id,
                        date=e.date,
                        start_time=e.start_time,
                        end_time=e.end_time,
                        role_id=e.role_id,
                    )
                    for e in entries
                ],
                coverage=[
                    AgendaCoverageResponse(
                        id=c.id,
                        agenda_id=c.agenda_id,
                        date=c.date,
                        start_time=c.start_time,
                        end_time=c.end_time,
                        role_id=c.role_id,
                        is_covered=c.is_covered,
                        required_person_count=c.required_person_count,
                    )
                    for c in coverage
                ],
            )
        )

    return result

