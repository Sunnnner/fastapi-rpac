

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from persist.models.permission_model import Permission
from persist.permission_dao import PermissionDao
from services.model.permission_vo import PermissionCreate


class PermissionService:
    def __init__(self, session: AsyncSession, permission_dao: PermissionDao):
        self.session = session
        self.permission_dao = permission_dao

    async def create_permission(self, permission: PermissionCreate) -> Permission:
        permission_exist = await self.permission_dao.get_permission_by_name(permission.name)
        if permission_exist:
            raise HTTPException(status_code=400, detail="权限已存在")
        permission = Permission(
            name=permission.name,
            description=permission.description,
        )
        return await self.permission_dao.create_permission(permission)