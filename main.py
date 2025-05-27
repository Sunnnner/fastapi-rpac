from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
from routers import routers
from services import ServiceContainer

# 导入中间件
from middleware import (
    AuthMiddleware,
    LoggingMiddleware,
    CORSMiddleware,
    ErrorHandlerMiddleware
)

container = ServiceContainer()
container.wire([*routers])
api_prefix = os.getenv("API_PREFIX", "/api/v1")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title='rpac', lifespan=lifespan)

# 添加中间件（注意顺序：后添加的先执行）
# 执行顺序: CORS -> ErrorHandler -> Logging -> Auth -> 路由处理

# 1. 身份验证中间件（最后执行，除了路由处理）
app.add_middleware(
    AuthMiddleware,
    token_service=container.token_service()  # 注入TokenService
)

# 2. 请求日志中间件
app.add_middleware(LoggingMiddleware)

# 3. 错误处理中间件
app.add_middleware(ErrorHandlerMiddleware)

# 4. CORS中间件（最先执行）
app.add_middleware(CORSMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health")
async def health_check():
    """健康检查端点，不需要认证"""
    return {"status": "healthy", "service": "fastapi-rpac"}

for r in routers:
    app.include_router(r.router, prefix=api_prefix)