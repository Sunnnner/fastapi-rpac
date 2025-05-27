from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from persist.models.role_model import Role
from persist.role_dao import RoleDao
from services.model.role_vo import RoleCreate, RolePermission



class RoleService:
    def __init__(self, session: AsyncSession, role_dao: RoleDao):
        self.session = session
        self.role_dao = role_dao

    
    async def add_permission_to_role(self, role_permission: RolePermission) -> Role:
        role_exist = await self.role_dao.get_role_by_id(role_permission.role_id)
        if not role_exist:
            raise HTTPException(status_code=400, detail="角色不存在")
        permission_exist = await self.permission_dao.get_permission_by_id(role_permission.permission_id)
        if not permission_exist:
            raise HTTPException(status_code=400, detail="权限不存在")

        role = await self.role_dao.add_permission_to_role(role_permission.role_id, role_permission.permission_id)
        return {"role": role.name, "permission": [permission.name for permission in role.permissions]}
    
    
    async def create_role(self, role: RoleCreate) -> Role:
        role_exist = await self.role_dao.get_role_by_name(role.name)
        if role_exist:
            raise HTTPException(status_code=400, detail="角色已存在")
        role = Role(
            name=role.name,
            description=role.description,
        )
        return await self.role_dao.create_role(role)