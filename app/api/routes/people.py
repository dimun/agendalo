from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_person_service
from app.domain.schemas import PersonCreate, PersonResponse
from app.services.person_service import PersonService

router = APIRouter(prefix="/api/people", tags=["people"])


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def create_person(
    person_data: PersonCreate,
    person_service: PersonService = Depends(get_person_service),
):
    person = person_service.create_person(person_data)
    return PersonResponse(
        id=person.id,
        name=person.name,
        email=person.email,
    )


@router.get("", response_model=list[PersonResponse])
def get_all_people(
    person_service: PersonService = Depends(get_person_service),
):
    people = person_service.get_all_people()
    return [
        PersonResponse(id=p.id, name=p.name, email=p.email) for p in people
    ]


@router.get("/{person_id}", response_model=PersonResponse)
def get_person(
    person_id: UUID,
    person_service: PersonService = Depends(get_person_service),
):
    person = person_service.get_person(person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return PersonResponse(id=person.id, name=person.name, email=person.email)

