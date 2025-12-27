from uuid import UUID, uuid4

from modules.main_backend.domain.models import Role
from modules.main_backend.domain.schemas import RoleCreate
from modules.main_backend.repositories.interfaces import RoleRepository


class RoleService:
    def __init__(self, role_repository: RoleRepository):
        self.role_repository = role_repository

    def create_role(self, role_data: RoleCreate) -> Role:
        role = Role(
            id=uuid4(),
            name=role_data.name,
            description=role_data.description,
        )
        return self.role_repository.create(role)

    def get_role(self, role_id: UUID) -> Role | None:
        return self.role_repository.get_by_id(role_id)

    def get_all_roles(self) -> list[Role]:
        return self.role_repository.get_all()

