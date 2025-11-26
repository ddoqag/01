"""
FastAPI 应用工厂 - 展示现代 Python Web 框架配置和中间件
"""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import structlog

from ..core.config import get_settings
from ..core.exceptions import AIPlatformError
from .middleware import setup_middleware
from .routes import api_router
from ..services import AIService, ConversationService

# Python 3.13: 结构化日志配置
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - Python 3.13 异步上下文管理器"""
    settings = get_settings()

    # 启动时初始化
    logger.info("Starting AI Platform application", version=settings.app_version)

    try:
        # 初始化 AI 服务
        ai_service = AIService()
        await ai_service.initialize()
        app.state.ai_service = ai_service

        # 初始化对话服务
        conversation_service = ConversationService()
        await conversation_service.initialize()
        app.state.conversation_service = conversation_service

        logger.info("Application startup completed")

    except Exception as e:
        logger.error("Failed to initialize application", error=str(e))
        raise

    yield

    # 关闭时清理
    logger.info("Shutting down AI Platform application")

    try:
        if hasattr(app.state, 'ai_service'):
            await app.state.ai_service.cleanup()
        if hasattr(app.state, 'conversation_service'):
            await app.state.conversation_service.cleanup()

        logger.info("Application shutdown completed")

    except Exception as e:
        logger.error("Error during application shutdown", error=str(e))

def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""
    settings = get_settings()

    # 创建 FastAPI 应用
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="现代化 AI 集成平台 - 展示 Python 3.13+ 特性",
        docs_url="/docs" if settings.is_development() else None,
        redoc_url="/redoc" if settings.is_development() else None,
        openapi_url="/openapi.json" if settings.is_development() else None,
        lifespan=lifespan,
    )

    # 设置中间件
    setup_middleware(app)

    # 注册路由
    app.include_router(api_router, prefix="/api/v1")

    # 添加健康检查端点
    app.add_route("/health", health_check, methods=["GET"])

    # 添加根路径
    app.add_route("/", root_endpoint, methods=["GET"])

    # 异常处理器
    register_exception_handlers(app)

    return app

# 创建应用实例
app = create_app()

def setup_middleware(app: FastAPI) -> None:
    """设置应用中间件"""
    settings = get_settings()

    # CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Gzip 压缩中间件
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # 自定义中间件
    from .middleware import (
        RequestLoggingMiddleware,
        RateLimitMiddleware,
        SecurityHeadersMiddleware,
        MetricsMiddleware,
    )

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(SecurityHeadersMiddleware)

    if settings.enable_metrics:
        app.add_middleware(MetricsMiddleware)

def register_exception_handlers(app: FastAPI) -> None:
    """注册全局异常处理器"""

    @app.exception_handler(AIPlatformError)
    async def ai_platform_exception_handler(request: Request, exc: AIPlatformError):
        """处理平台异常"""
        return JSONResponse(
            status_code=400,
            content=exc.to_dict(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        """处理值错误"""
        return JSONResponse(
            status_code=400,
            content={
                "error_type": "ValueError",
                "error_code": "INVALID_VALUE",
                "message": str(exc),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """处理未捕获的异常"""
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error_type": "InternalServerError",
                "error_code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
        )

async def health_check(request: Request) -> JSONResponse:
    """健康检查端点"""
    try:
        # 检查服务状态
        ai_service_status = "healthy"
        conversation_service_status = "healthy"

        if hasattr(request.app.state, 'ai_service'):
            # 可以添加更详细的健康检查
            pass
        else:
            ai_service_status = "unhealthy"

        if hasattr(request.app.state, 'conversation_service'):
            pass
        else:
            conversation_service_status = "unhealthy"

        overall_status = "healthy" if (
            ai_service_status == "healthy" and
            conversation_service_status == "healthy"
        ) else "unhealthy"

        return JSONResponse(
            status_code=200 if overall_status == "healthy" else 503,
            content={
                "status": overall_status,
                "version": get_settings().app_version,
                "services": {
                    "ai_service": ai_service_status,
                    "conversation_service": conversation_service_status,
                },
                "timestamp": structlog.processors.TimeStamper().format_timestamp(),
            },
        )

    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": structlog.processors.TimeStamper().format_timestamp(),
            },
        )

async def root_endpoint(request: Request) -> JSONResponse:
    """根路径端点"""
    settings = get_settings()

    return JSONResponse(
        content={
            "message": f"Welcome to {settings.app_name}",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs_url": "/docs" if settings.is_development() else None,
            "health_url": "/health",
        },
    )

# Python 3.13: 异步上下文管理器用于依赖注入
class ServiceManager:
    """服务管理器 - 用于依赖注入"""

    def __init__(self, app: FastAPI):
        self.app = app

    async def get_ai_service(self) -> AIService:
        """获取 AI 服务实例"""
        if not hasattr(self.app.state, 'ai_service'):
            raise RuntimeError("AI service not initialized")
        return self.app.state.ai_service

    async def get_conversation_service(self) -> ConversationService:
        """获取对话服务实例"""
        if not hasattr(self.app.state, 'conversation_service'):
            raise RuntimeError("Conversation service not initialized")
        return self.app.state.conversation_service

# Python 3.13: 使用 Protocol 进行类型检查
from typing import Protocol

class HasState(Protocol):
    """具有状态属性的对象协议"""
    state: Any

def get_service_from_state[T](
    request: Request,
    service_name: str,
    service_type: type[T],
) -> T:
    """从应用状态获取服务"""
    app = request.app
    if not isinstance(app, HasState):
        raise RuntimeError("Application does not have state")

    if not hasattr(app.state, service_name):
        raise RuntimeError(f"Service {service_name} not initialized")

    service = getattr(app.state, service_name)
    if not isinstance(service, service_type):
        raise RuntimeError(f"Service {service_name} is not of type {service_type.__name__}")

    return service