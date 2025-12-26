from uuid import UUID, uuid4

from app.domain.models import Person
from app.domain.schemas import PersonCreate
from app.repositories.interfaces import PersonRepository


class PersonService:
    def __init__(self, person_repository: PersonRepository):
        self.person_repository = person_repository

    def create_person(self, person_data: PersonCreate) -> Person:
        person = Person(
            id=uuid4(),
            name=person_data.name,
            email=person_data.email,
        )
        return self.person_repository.create(person)

    def get_person(self, person_id: UUID) -> Person | None:
        return self.person_repository.get_by_id(person_id)

    def get_all_people(self) -> list[Person]:
        return self.person_repository.get_all()

    def update_person(self, person_id: UUID, person_data: PersonCreate) -> Person | None:
        person = self.person_repository.get_by_id(person_id)
        if not person:
            return None
        person.name = person_data.name
        person.email = person_data.email
        return self.person_repository.update(person)

    def delete_person(self, person_id: UUID) -> bool:
        return self.person_repository.delete(person_id)

