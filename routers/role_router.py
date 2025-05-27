from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject

from persist.models.role_model import Role
from services import ServiceContainer
from services.model.role_vo import RoleCreate, RolePermission
from services.role_service import RoleService


router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/{role_id}/permissions")
@inject
async def add_permission_to_role(
    role_permission: RolePermission,
    role_service: RoleService = Depends(Provide[ServiceContainer.role_service]),
) -> Role:
    return await role_service.add_permission_to_role(role_permission)

@router.post("/create")
@inject
async def create_role(
    role: RoleCreate,
    role_service: RoleService = Depends(Provide[ServiceContainer.role_service]),
) -> Role:
    return await role_service.create_role(role)