from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from persist.models.user_model import User
from persist.role_dao import RoleDao
from persist.user_dao import UserDao
from services.model.user_vo import UserCreate, UserLogin, UserRole
from services.token_service import TokenService
from utils.bcrypt import hash_password, verify_password


class UserService:
    def __init__(self, session: AsyncSession, user_dao: UserDao, token_service: TokenService, role_dao: RoleDao):
        self.session = session
        self.user_dao = user_dao
        self.token_service = token_service
        self.role_dao = role_dao

    async def add_role_to_user(self, user_role: UserRole) -> User:
        user_exist = await self.user_dao.get_user_by_id(user_role.user_id)
        if not user_exist:
            raise HTTPException(status_code=400, detail="用户不存在")
        role_exist = await self.role_dao.get_role_by_id(user_role.role_id)
        if not role_exist:
            raise HTTPException(status_code=400, detail="角色不存在")
        user = await self.user_dao.add_role_to_user(user_role.user_id, user_role.role_id)
        return {"username": user.username, "role": [role.name for role in user.roles]}
    
    async def create_user(self, user: UserCreate) -> User:
        user_exist = await self.user_dao.get_user_by_username(user.username)
        if user_exist:
            raise HTTPException(status_code=400, detail="用户已存在")
        user = User(
            username=user.username,
            password=hash_password(user.password),
            email=user.email,
        )
        return await self.user_dao.create_user(user)
    
    async def login(self, user: UserLogin) -> User:
        user_exist = await self.user_dao.get_user_by_username(user.username)
        if not user_exist:
            raise HTTPException(status_code=400, detail="用户不存在")
        if not verify_password(user.password, user_exist.password):
            raise HTTPException(status_code=400, detail="密码错误")
        return self.token_service.generate_token(user_exist)