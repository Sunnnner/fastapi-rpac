from fastapi import APIRouter, Depends

from dependency_injector.wiring import Provide, inject

from persist.models.user_model import User
from services import ServiceContainer
from services.model.user_vo import UserCreate, UserLogin, UserRole
from services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/{user_id}/roles")
@inject
async def add_role_to_user(
    user_role: UserRole,
    user_service: UserService = Depends(Provide[ServiceContainer.user_service]),
) -> User:
    return await user_service.add_role_to_user(UserRole)


@router.post("/register")
@inject
async def register(
    user: UserCreate,
    user_service: UserService = Depends(Provide[ServiceContainer.user_service]),
) -> User:
    """
    注册用户

    Args:
        user (UserCreate): 用户注册信息
        user_service (UserService, optional): 用户服务. Defaults to Depends(Provide[ServiceContainer.user_service]).
    """
    return await user_service.create_user(user)


@router.post("/login")
@inject
async def login(
    user: UserLogin,
    user_service: UserService = Depends(Provide[ServiceContainer.user_service]),
) -> User:
    return await user_service.login(user)