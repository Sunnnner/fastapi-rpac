from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject

from persist.models.permission_model import Permission
from services import ServiceContainer
from services.model.permission_vo import PermissionCreate
from services.permission_service import PermissionService


router = APIRouter(prefix="/permissions", tags=["permissions"])


@router.post("/create")
@inject
async def create_permission(
    permission: PermissionCreate,
    permission_service: PermissionService = Depends(Provide[ServiceContainer.permission_service]),
) -> Permission:
    return await permission_service.create_permission(permission)