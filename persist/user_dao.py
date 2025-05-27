from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from persist.models.role_model import Role
from persist.models.user_model import User


class UserDao:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_role_to_user(self, user_id: int, role_id: int) -> User:
        async with self.session() as session:
            user = await session.get(User, user_id)
            role = await session.get(Role, role_id)
            user.roles.append(role)
            await session.commit()
            return user
    
    async def get_user_by_id(self, user_id: int) -> User:   
        async with self.session() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one_or_none()
    
    async def create_user(self, user: User) -> User:
        async with self.session() as session:
            session.add(user)
            await session.commit()
            return user
    
    async def get_user_by_username(self, username: str):
        async with self.session() as session:
            result = await session.execute(select(User).where(User.username == username))
            return result.scalar_one_or_none()