

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from persist.models.permission_model import Permission


class PermissionDao:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_permission(self, permission: Permission) -> Permission:
        async with self.session() as session:
            session.add(permission)
            await session.commit()
            return permission
        
    async def get_permission_by_name(self, name: str) -> Permission:
        async with self.session() as session:
            result = await session.execute(select(Permission).where(Permission.name == name))
            return result.scalar_one_or_none()