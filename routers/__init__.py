from routers import (
    user_router,
    role_router,
    permission_router,
)

routers = [
    user_router,
    role_router,
    permission_router,
]

__all__ = [
    "routers",
]