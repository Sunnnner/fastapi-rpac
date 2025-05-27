import traceback
import logging
from typing import Dict, Any
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError


# 配置错误日志记录器
error_logger = logging.getLogger("ErrorHandler")


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    异步错误处理中间件
    统一处理应用中的异常，返回标准化的错误响应
    """
    
    def __init__(self, app):
        super().__init__(app)
        self.include_details = self._should_include_details()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        异步处理请求，捕获并处理所有异常
        """
        try:
            response = await call_next(request)
            return response
            
        except HTTPException as e:
            # FastAPI HTTP异常
            return await self._handle_http_exception(request, e)
            
        except ValidationError as e:
            # Pydantic验证异常
            return await self._handle_validation_error(request, e)
            
        except SQLAlchemyError as e:
            # 数据库异常
            return await self._handle_database_error(request, e)
            
        except Exception as e:
            # 其他未捕获的异常
            return await self._handle_general_exception(request, e)
    
    async def _handle_http_exception(self, request: Request, exc: HTTPException) -> JSONResponse:
        """
        处理FastAPI HTTP异常
        """
        error_data = {
            "error": {
                "type": "HTTPException",
                "code": exc.status_code,
                "message": exc.detail,
                "timestamp": self._get_timestamp(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        # 记录警告级别日志（4xx错误）或错误级别日志（5xx错误）
        log_message = f"HTTP {exc.status_code}: {exc.detail} - {request.method} {request.url.path}"
        if exc.status_code >= 500:
            error_logger.error(log_message)
        else:
            error_logger.warning(log_message)
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_data
        )
    
    async def _handle_validation_error(self, request: Request, exc: ValidationError) -> JSONResponse:
        """
        处理Pydantic验证错误
        """
        # 格式化验证错误
        validation_errors = []
        for error in exc.errors():
            validation_errors.append({
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"]
            })
        
        error_data = {
            "error": {
                "type": "ValidationError",
                "code": 422,
                "message": "请求数据验证失败",
                "timestamp": self._get_timestamp(),
                "path": request.url.path,
                "method": request.method,
                "validation_errors": validation_errors
            }
        }
        
        error_logger.warning(f"验证错误 - {request.method} {request.url.path}: {validation_errors}")
        
        return JSONResponse(
            status_code=422,
            content=error_data
        )
    
    async def _handle_database_error(self, request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """
        处理数据库异常
        """
        error_id = self._generate_error_id()
        
        error_data = {
            "error": {
                "type": "DatabaseError", 
                "code": 500,
                "message": "数据库操作失败",
                "timestamp": self._get_timestamp(),
                "path": request.url.path,
                "method": request.method,
                "error_id": error_id
            }
        }
        
        # 开发环境包含详细错误信息
        if self.include_details:
            error_data["error"]["details"] = str(exc)
        
        # 记录详细的数据库错误
        error_logger.error(
            f"数据库错误 [{error_id}] - {request.method} {request.url.path}: {str(exc)}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=500,
            content=error_data
        )
    
    async def _handle_general_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """
        处理一般异常
        """
        error_id = self._generate_error_id()
        
        error_data = {
            "error": {
                "type": "InternalServerError",
                "code": 500,
                "message": "服务器内部错误",
                "timestamp": self._get_timestamp(),
                "path": request.url.path,
                "method": request.method,
                "error_id": error_id
            }
        }
        
        # 开发环境包含详细错误信息
        if self.include_details:
            error_data["error"]["details"] = str(exc)
            error_data["error"]["exception_type"] = type(exc).__name__
        
        # 记录详细的异常信息
        error_logger.error(
            f"未处理异常 [{error_id}] - {request.method} {request.url.path}: {str(exc)}\n"
            f"异常类型: {type(exc).__name__}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        return JSONResponse(
            status_code=500,
            content=error_data
        )
    
    def _get_timestamp(self) -> str:
        """
        获取当前时间戳
        """
        import time
        return time.strftime("%Y-%m-%d %H:%M:%S")
    
    def _generate_error_id(self) -> str:
        """
        生成唯一的错误ID用于追踪
        """
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _should_include_details(self) -> bool:
        """
        根据环境决定是否包含详细错误信息
        """
        import os
        environment = os.getenv("ENVIRONMENT", "development").lower()
        return environment in ["development", "dev", "debug"]
    
    async def _log_request_context(self, request: Request) -> Dict[str, Any]:
        """
        记录请求上下文信息，用于错误排查
        """
        context = {
            "url": str(request.url),
            "method": request.method,
            "headers": dict(request.headers),
            "query_params": dict(request.query_params),
            "client_ip": getattr(request.client, "host", "unknown"),
            "user_id": getattr(request.state, "user_id", None),
            "authenticated": getattr(request.state, "authenticated", False)
        }
        
        return context 