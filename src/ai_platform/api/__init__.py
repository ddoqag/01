"""
API 模块 - FastAPI Web 接口
"""

from .app import create_app, app
from .routes import api_router
from .middleware import setup_middleware
from .dependencies import get_ai_service, get_conversation_service

__all__ = [
    "create_app",
    "app",
    "api_router",
    "setup_middleware",
    "get_ai_service",
    "get_conversation_service",
]