from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from persist.models.permission_model import Permission
from persist.models.role_model import Role

class RoleDao:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_permission_to_role(self, role_id: int, permission_id: int) -> Role:
        async with self.session() as session:
            role = await session.get(Role, role_id)
            permission = await session.get(Permission, permission_id)
            role.permissions.append(permission)
            await session.commit()
            return role
    
    async def get_role_by_id(self, role_id: int) -> Role:
        async with self.session() as session:
            result = await session.execute(select(Role).where(Role.id == role_id))
            return result.scalar_one_or_none()
    
    async def create_role(self, role: Role) -> Role:
        async with self.session() as session:
            session.add(role)
            await session.commit()
            return role
        
    async def get_role_by_name(self, name: str) -> Role:
        async with self.session() as session:
            result = await session.execute(select(Role).where(Role.name == name))
            return result.scalar_one_or_none()