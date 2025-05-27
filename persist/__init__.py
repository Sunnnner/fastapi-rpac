import os
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from persist.permission_dao import PermissionDao
from persist.role_dao import RoleDao
from persist.user_dao import UserDao


class PersistContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    pg_client = providers.Singleton(
        create_async_engine,
        os.getenv("POSTGRES_ASYNC_DATABASE_URL", "postgresql+asyncpg://kws:k123456@localhost:5432/rpac"),
        pool_size=10,
        max_overflow=20,
    )
    
    db_session_factory = providers.Singleton(
        sessionmaker,
        bind=pg_client,
        class_=AsyncSession, # 异步会话
        expire_on_commit=False, # 关闭自动提交
    )
    
    session = providers.Factory(
        db_session_factory,
    )
    
    user_dao = providers.Singleton(
        UserDao,
        session=session,
    )
    
    role_dao = providers.Singleton(
        RoleDao,
        session=session,
    )
    
    permission_dao = providers.Singleton(
        PermissionDao,
        session=session,
    )