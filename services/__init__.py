import os
from persist import PersistContainer
from dependency_injector import containers, providers

from services.permission_service import PermissionService
from services.role_service import RoleService
from services.token_service import TokenService
from services.user_service import UserService
SECRET_KEY = os.getenv("SECRET_KEY", default="97548834e9fe67fc52c597958581362fdd0b53a6abeda7965f698627599552b6")

class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    persist_container = providers.Container(
        PersistContainer,
        config=config,
    )
    
    token_service = providers.Singleton(
        TokenService,
        secret_key=SECRET_KEY,
    )
    
    user_service = providers.Singleton(
        UserService,
        session=persist_container.session,
        user_dao=persist_container.user_dao,
        token_service=token_service,
    )
    
    role_service = providers.Singleton(
        RoleService,
        session=persist_container.session,
        role_dao=persist_container.role_dao,
    )
    
    permission_service = providers.Singleton(
        PermissionService,
        session=persist_container.session,
        permission_dao=persist_container.permission_dao,
    )