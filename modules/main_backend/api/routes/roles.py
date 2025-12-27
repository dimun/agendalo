from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from modules.main_backend.api.dependencies import get_role_service
from modules.main_backend.domain.schemas import RoleCreate, RoleResponse
from modules.main_backend.services.role_service import RoleService

router = APIRouter(prefix="/api/roles", tags=["roles"])


@router.post("", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreate,
    role_service: RoleService = Depends(get_role_service),
):
    role = role_service.create_role(role_data)
    return RoleResponse(
        id=role.id,
        name=role.name,
        description=role.description,
    )


@router.get("", response_model=list[RoleResponse])
def get_all_roles(
    role_service: RoleService = Depends(get_role_service),
):
    roles = role_service.get_all_roles()
    return [
        RoleResponse(id=r.id, name=r.name, description=r.description)
        for r in roles
    ]


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: UUID,
    role_service: RoleService = Depends(get_role_service),
):
    role = role_service.get_role(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    return RoleResponse(id=role.id, name=role.name, description=role.description)

