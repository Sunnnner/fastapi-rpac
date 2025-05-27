import time
import logging
import json
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


# 配置日志记录器
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/requests.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("RequestLogger")


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    异步请求日志中间件
    记录所有HTTP请求和响应的详细信息
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.exclude_paths = {
            "/health",
            "/metrics", 
            "/favicon.ico"
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        异步处理请求，记录详细的请求和响应信息
        """
        # 跳过不需要记录的路径
        if request.url.path in self.exclude_paths:
            return await call_next(request)
        
        # 记录请求开始时间
        start_time = time.time()
        
        # 收集请求信息
        request_info = await self._collect_request_info(request)
        
        # 处理请求
        response = await call_next(request)
        
        # 计算处理时间
        process_time = time.time() - start_time
        
        # 收集响应信息
        response_info = self._collect_response_info(response, process_time)
        
        # 记录完整的请求-响应日志
        await self._log_request_response(request_info, response_info)
        
        # 添加响应头
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
    
    async def _collect_request_info(self, request: Request) -> Dict[str, Any]:
        """
        收集请求信息
        """
        # 安全地读取请求体
        body = b""
        try:
            body = await request.body()
        except Exception as e:
            logger.warning(f"无法读取请求体: {e}")
        
        # 过滤敏感信息的请求头
        filtered_headers = self._filter_sensitive_headers(dict(request.headers))
        
        return {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": filtered_headers,
            "body_size": len(body),
            "body": self._safe_decode_body(body),
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "user_id": getattr(request.state, "user_id", None),
            "authenticated": getattr(request.state, "authenticated", False)
        }
    
    def _collect_response_info(self, response: Response, process_time: float) -> Dict[str, Any]:
        """
        收集响应信息
        """
        return {
            "status_code": response.status_code,
            "process_time": round(process_time, 4),
            "response_headers": dict(response.headers),
            "content_length": response.headers.get("content-length", "0")
        }
    
    async def _log_request_response(self, request_info: Dict[str, Any], response_info: Dict[str, Any]):
        """
        记录完整的请求-响应日志
        """
        log_data = {
            "request": request_info,
            "response": response_info
        }
        
        # 根据状态码决定日志级别
        status_code = response_info["status_code"]
        log_message = (
            f'{request_info["method"]} {request_info["path"]} '
            f'- {status_code} - {response_info["process_time"]}s'
        )
        
        if status_code >= 500:
            logger.error(f"{log_message}\n详细信息: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        elif status_code >= 400:
            logger.warning(f"{log_message}\n详细信息: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
        else:
            logger.info(f"{log_message}")
            # 详细信息只在DEBUG级别记录，避免日志过于冗长
            logger.debug(f"详细信息: {json.dumps(log_data, ensure_ascii=False, indent=2)}")
    
    def _filter_sensitive_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """
        过滤敏感的请求头信息
        """
        sensitive_headers = {"authorization", "cookie", "x-api-key"}
        filtered = {}
        
        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                filtered[key] = "***FILTERED***"
            else:
                filtered[key] = value
        
        return filtered
    
    def _safe_decode_body(self, body: bytes) -> str:
        """
        安全地解码请求体
        """
        if not body:
            return ""
        
        try:
            # 尝试解码为JSON
            decoded = body.decode("utf-8")
            json.loads(decoded)  # 验证是否为有效JSON
            return decoded
        except (UnicodeDecodeError, json.JSONDecodeError):
            # 如果不是有效的JSON或无法解码，返回base64编码
            import base64
            return f"<binary data: {base64.b64encode(body[:100]).decode()}...>"
    
    def _get_client_ip(self, request: Request) -> str:
        """
        获取客户端真实IP地址
        """
        # 检查代理头
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # 返回直接连接的客户端IP
        return getattr(request.client, "host", "unknown") 