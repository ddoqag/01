"""
AI Engineer Framework 主应用入口

提供FastAPI应用和完整的AI工程化服务
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import api_router
from .api.middleware import (
    LoggingMiddleware,
    RateLimitMiddleware,
    SecurityMiddleware,
    MetricsMiddleware
)
from .utils.config import load_config
from .utils.logging import setup_logging
from .services.factory import ServiceFactory
from .services.monitoring_service import init_monitoring, get_monitoring_service
from .services.cost_optimizer import init_cost_optimizer, get_cost_optimizer


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger = logging.getLogger(__name__)
    logger.info("Starting AI Engineer Framework...")

    try:
        # 加载配置
        config = load_config()

        # 初始化监控服务
        monitoring_config = config.get("monitoring", {})
        monitoring_service = await init_monitoring(monitoring_config)
        app.state.monitoring_service = monitoring_service

        # 初始化成本优化器
        cost_config = config.get("cost_optimization", {})
        cost_optimizer = await init_cost_optimizer(cost_config)
        app.state.cost_optimizer = cost_optimizer

        # 初始化服务工厂
        service_factory = ServiceFactory()
        app.state.service_factory = service_factory

        # 预热服务
        await warmup_services(service_factory, config)

        logger.info("AI Engineer Framework started successfully")
        yield

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise

    finally:
        # 关闭时清理
        logger.info("Shutting down AI Engineer Framework...")
        await cleanup_services(app)
        logger.info("AI Engineer Framework stopped")


async def warmup_services(service_factory: ServiceFactory, config: dict) -> None:
    """预热服务"""
    logger = logging.getLogger(__name__)

    # 预热默认LLM服务
    default_llm = config.get("default_llm")
    if default_llm:
        try:
            from ..models.llm import LLMConfig
            llm_config = LLMConfig(**config["llm_providers"][default_llm])
            await service_factory.create_llm_provider(llm_config)
            logger.info(f"LLM service '{default_llm}' warmed up")
        except Exception as e:
            logger.warning(f"Failed to warm up LLM service '{default_llm}': {e}")

    # 预热默认嵌入服务
    default_embedding = config.get("default_embedding")
    if default_embedding:
        try:
            from ..models.embeddings import EmbeddingConfig
            embedding_config = EmbeddingConfig(**config["embedding_providers"][default_embedding])
            await service_factory.create_embedding_provider(embedding_config)
            logger.info(f"Embedding service '{default_embedding}' warmed up")
        except Exception as e:
            logger.warning(f"Failed to warm up embedding service '{default_embedding}': {e}")

    # 预热默认向量存储
    default_vector_store = config.get("default_vector_store")
    if default_vector_store:
        try:
            from ..models.embeddings import VectorStoreConfig
            store_config = VectorStoreConfig(**config["vector_stores"][default_vector_store])
            await service_factory.create_vector_store(store_config)
            logger.info(f"Vector store '{default_vector_store}' warmed up")
        except Exception as e:
            logger.warning(f"Failed to warm up vector store '{default_vector_store}': {e}")


async def cleanup_services(app: FastAPI) -> None:
    """清理服务"""
    try:
        # 清理服务工厂
        if hasattr(app.state, "service_factory"):
            await app.state.service_factory.cleanup_all()

        # 清理监控服务
        if hasattr(app.state, "monitoring_service"):
            await app.state.monitoring_service.stop()

    except Exception as e:
        logging.getLogger(__name__).error(f"Error during service cleanup: {e}")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    # 加载配置
    config = load_config()

    # 设置日志
    setup_logging(config.get("app", {}).get("log_level", "INFO"))

    # 创建FastAPI应用
    app_config = config.get("app", {})
    app = FastAPI(
        title=app_config.get("name", "AI Engineer Framework"),
        version=app_config.get("version", "0.1.0"),
        description="现代AI工程化框架 - 集成多LLM提供商、RAG系统、Agent和多模态能力",
        lifespan=lifespan,
        docs_url="/docs" if app_config.get("documentation_enabled", True) else None,
        redoc_url="/redoc" if app_config.get("documentation_enabled", True) else None,
    )

    # 添加中间件
    setup_middleware(app, config)

    # 添加路由
    api_config = config.get("api", {})
    prefix = api_config.get("prefix", "/api/v1")
    app.include_router(api_router, prefix=prefix)

    # 添加异常处理器
    setup_exception_handlers(app)

    # 添加健康检查端点
    setup_health_endpoints(app)

    return app


def setup_middleware(app: FastAPI, config: dict) -> None:
    """设置中间件"""
    # CORS中间件
    security_config = config.get("security", {})
    if security_config.get("cors_enabled", True):
        origins = security_config.get("cors_origins", ["*"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # 可信主机中间件
    if not config.get("app", {}).get("debug", False):
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*"]
        )

    # 自定义中间件
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(MetricsMiddleware)

    if security_config.get("rate_limit_enabled", True):
        app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=security_config.get("rate_limit_requests_per_minute", 60)
        )

    if security_config.get("api_key_required", False):
        app.add_middleware(SecurityMiddleware)


def setup_exception_handlers(app: FastAPI) -> None:
    """设置异常处理器"""
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logging.getLogger(__name__).error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "detail": str(exc) if app.debug else "An unexpected error occurred"
            }
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        return JSONResponse(
            status_code=404,
            content={
                "error": "Not found",
                "detail": "The requested resource was not found"
            }
        )

    @app.exception_handler(429)
    async def rate_limit_handler(request: Request, exc):
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "detail": "Too many requests, please try again later"
            }
        )


def setup_health_endpoints(app: FastAPI) -> None:
    """设置健康检查端点"""

    @app.get("/health")
    async def health_check():
        """基础健康检查"""
        return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

    @app.get("/health/detailed")
    async def detailed_health_check():
        """详细健康检查"""
        health_status = {
            "status": "healthy",
            "timestamp": asyncio.get_event_loop().time(),
            "services": {}
        }

        # 检查监控服务
        try:
            monitoring_service = get_monitoring_service()
            if monitoring_service:
                health_status["services"]["monitoring"] = await monitoring_service.health_check()
        except Exception as e:
            health_status["services"]["monitoring"] = False

        # 检查成本优化器
        try:
            cost_optimizer = get_cost_optimizer()
            if cost_optimizer:
                health_status["services"]["cost_optimizer"] = True
        except Exception as e:
            health_status["services"]["cost_optimizer"] = False

        return health_status

    @app.get("/metrics")
    async def metrics():
        """获取系统指标"""
        try:
            monitoring_service = get_monitoring_service()
            if monitoring_service:
                return monitoring_service.get_monitoring_summary()
        except Exception as e:
            return {"error": "Metrics not available"}

    @app.get("/stats")
    async def system_stats():
        """获取系统统计信息"""
        stats = {
            "cost_summary": {},
            "system_info": {}
        }

        try:
            cost_optimizer = get_cost_optimizer()
            if cost_optimizer:
                stats["cost_summary"] = cost_optimizer.get_cost_summary()
        except Exception as e:
            stats["cost_summary"] = {"error": "Cost data not available"}

        return stats


# 创建应用实例
app = create_app()


def main():
    """主函数"""
    config = load_config()
    app_config = config.get("app", {})

    uvicorn.run(
        "src.main:app",
        host=app_config.get("host", "0.0.0.0"),
        port=app_config.get("port", 8000),
        reload=app_config.get("debug", False),
        workers=1 if app_config.get("debug", False) else app_config.get("workers", 4),
        log_level=app_config.get("log_level", "info").lower(),
        access_log=True,
    )


if __name__ == "__main__":
    main()