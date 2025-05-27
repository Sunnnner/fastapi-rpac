import os
from typing import List, Set
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import PlainTextResponse


class CORSMiddleware(BaseHTTPMiddleware):
    """
    异步CORS中间件
    处理跨域资源共享请求，支持预检请求
    """
    
    def __init__(
        self,
        app,
        allow_origins: List[str] = None,
        allow_methods: List[str] = None,
        allow_headers: List[str] = None,
        allow_credentials: bool = True,
        expose_headers: List[str] = None,
        max_age: int = 86400
    ):
        super().__init__(app)
        
        # 从环境变量获取配置，提供默认值
        self.allow_origins = allow_origins or self._get_allowed_origins()
        self.allow_methods = allow_methods or [
            "GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"
        ]
        self.allow_headers = allow_headers or [
            "Accept",
            "Accept-Language", 
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-API-Key"
        ]
        self.allow_credentials = allow_credentials
        self.expose_headers = expose_headers or ["X-Process-Time"]
        self.max_age = max_age
        
        # 转换为集合以提高查找性能
        self.allow_origins_set: Set[str] = set(self.allow_origins)
        self.allow_methods_set: Set[str] = set(self.allow_methods)
        self.allow_headers_set: Set[str] = {header.lower() for header in self.allow_headers}
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        异步处理CORS请求
        """
        origin = request.headers.get("origin")
        
        # 处理预检请求
        if request.method == "OPTIONS":
            return self._handle_preflight_request(request, origin)
        
        # 处理实际请求
        response = await call_next(request)
        
        # 添加CORS头
        self._add_cors_headers(response, origin)
        
        return response
    
    def _handle_preflight_request(self, request: Request, origin: str) -> Response:
        """
        处理OPTIONS预检请求
        """
        # 检查来源是否被允许
        if not self._is_origin_allowed(origin):
            return PlainTextResponse(
                "CORS预检失败：来源不被允许",
                status_code=403
            )
        
        # 检查请求方法是否被允许
        request_method = request.headers.get("access-control-request-method")
        if request_method and request_method.upper() not in self.allow_methods_set:
            return PlainTextResponse(
                "CORS预检失败：请求方法不被允许",
                status_code=403
            )
        
        # 检查请求头是否被允许
        request_headers = request.headers.get("access-control-request-headers")
        if request_headers:
            headers = [h.strip().lower() for h in request_headers.split(",")]
            if not all(header in self.allow_headers_set for header in headers):
                return PlainTextResponse(
                    "CORS预检失败：请求头不被允许",
                    status_code=403
                )
        
        # 创建预检响应
        response = PlainTextResponse("CORS预检成功", status_code=200)
        self._add_cors_headers(response, origin, is_preflight=True)
        
        return response
    
    def _add_cors_headers(self, response: Response, origin: str, is_preflight: bool = False):
        """
        添加CORS响应头
        """
        if self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
        
        if self.allow_credentials:
            response.headers["Access-Control-Allow-Credentials"] = "true"
        
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        # 预检请求的特殊头
        if is_preflight:
            response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allow_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allow_headers)
            response.headers["Access-Control-Max-Age"] = str(self.max_age)
    
    def _is_origin_allowed(self, origin: str) -> bool:
        """
        检查来源是否被允许
        """
        if not origin:
            return False
        
        # 检查通配符
        if "*" in self.allow_origins_set:
            return True
        
        # 检查精确匹配
        if origin in self.allow_origins_set:
            return True
        
        # 检查模式匹配（支持子域名）
        for allowed_origin in self.allow_origins:
            if self._match_origin_pattern(origin, allowed_origin):
                return True
        
        return False
    
    def _match_origin_pattern(self, origin: str, pattern: str) -> bool:
        """
        匹配来源模式，支持通配符和子域名
        """
        # 支持 *.example.com 格式
        if pattern.startswith("*."):
            domain = pattern[2:]
            return origin.endswith(f".{domain}") or origin == domain
        
        return origin == pattern
    
    def _get_allowed_origins(self) -> List[str]:
        """
        从环境变量获取允许的来源列表
        """
        # 从环境变量获取，支持逗号分隔
        env_origins = os.getenv("CORS_ALLOWED_ORIGINS", "")
        if env_origins:
            return [origin.strip() for origin in env_origins.split(",")]
        
        # 开发环境默认配置
        if os.getenv("ENVIRONMENT", "development") == "development":
            return [
                "http://localhost:3000",    # React开发服务器
                "http://localhost:8080",    # Vue开发服务器
                "http://localhost:4200",    # Angular开发服务器
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:4200"
            ]
        
        # 生产环境需要明确配置
        return [] 