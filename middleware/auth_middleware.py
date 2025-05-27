import os
from typing import Optional
from fastapi import Request, Response, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

from services.token_service import TokenService


class AuthMiddleware(BaseHTTPMiddleware):
    """
    异步身份验证中间件
    验证JWT令牌并将用户信息注入到请求上下文中
    """
    
    def __init__(self, app, token_service: TokenService = None):
        super().__init__(app)
        self.token_service = token_service or TokenService(
            secret_key=os.getenv("SECRET_KEY", "97548834e9fe67fc52c597958581362fdd0b53a6abeda7965f698627599552b6")
        )
        self.security = HTTPBearer(auto_error=False)
        
        # 不需要认证的路径
        self.public_paths = {
            "/",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/api/v1/users/login",
            "/api/v1/users/register"
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        异步处理请求，验证身份并注入用户信息
        """
        # 检查是否为公开路径
        if self._is_public_path(request.url.path):
            return await call_next(request)
        
        # 提取并验证令牌
        token = self._extract_token(request)
        if token:
            try:
                # 验证令牌并获取用户信息
                payload = self.token_service.verify_token(token)
                # 将用户ID注入到请求状态中
                request.state.user_id = payload.get("sub")
                request.state.authenticated = True
            except HTTPException as e:
                # 令牌验证失败
                request.state.user_id = None
                request.state.authenticated = False
                # 对于需要认证的路径，返回401错误
                return Response(
                    content=f'{{"detail": "{e.detail}"}}',
                    status_code=e.status_code,
                    media_type="application/json"
                )
        else:
            # 没有提供令牌
            request.state.user_id = None
            request.state.authenticated = False
            return Response(
                content='{"detail": "未提供认证令牌"}',
                status_code=401,
                media_type="application/json"
            )
        
        # 继续处理请求
        response = await call_next(request)
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """
        检查路径是否为公开路径（不需要认证）
        """
        # 精确匹配
        if path in self.public_paths:
            return True
        
        # 路径前缀匹配（如静态文件）
        public_prefixes = ["/static", "/health"]
        return any(path.startswith(prefix) for prefix in public_prefixes)
    
    def _extract_token(self, request: Request) -> Optional[str]:
        """
        从请求中提取JWT令牌
        支持Authorization头和查询参数
        """
        # 从Authorization头提取
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            return authorization.split(" ")[1]
        
        # 从查询参数提取（备用方案）
        token = request.query_params.get("token")
        if token:
            return token
        
        return None 